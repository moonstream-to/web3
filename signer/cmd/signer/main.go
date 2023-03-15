package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"

	"github.com/gotk3/gotk3/glib"
	"github.com/gotk3/gotk3/gtk"
)

func getMsg(msgChan chan string, password, keyFilePath, rpcUri, contractAddress, fileInputPath, outputFilePath string, claimId int64) {
	privateContainer, err := initSigner2(password, keyFilePath)
	if err != nil {
		fmt.Println(err)
		msgChan <- ""
	}

	client, err := InitializeNetworkClient(rpcUri)
	if err != nil {
		fmt.Println(err)
		msgChan <- ""
	}

	contract := ContractDropper{}
	contract.SetContractAddress(contractAddress)
	err = contract.InitializeContractInstance(client)
	if err != nil {
		fmt.Println(err)
		msgChan <- ""
	}

	inputs, err := ParseInput(fileInputPath, false)
	if err != nil {
		fmt.Println(err)
		msgChan <- ""
	}

	var claimants []Claimant
	for _, input := range inputs {
		chm, err := contract.claimMessageHash(claimId, input.Address, input.ClaimBlockDeadline, input.Amount)
		if err != nil {
			fmt.Println(err)
			msgChan <- ""
		}
		sig, err := privateContainer.sign(chm)
		if err != nil {
			fmt.Println(err)
			msgChan <- ""
		}
		claimants = append(claimants, Claimant{
			ClaimantAddress:    input.Address,
			Amount:             input.Amount,
			Signature:          sig,
			ClaimBlockDeadline: input.ClaimBlockDeadline,
			ClaimId:            stateCLI.claimIdFlag,
		})
	}

	fullPath, err := ProcessOutput(claimants, outputFilePath, "csv")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	response := fmt.Sprintf("Output saved at: %s\nSigned by: %s\n", fullPath, privateContainer.publicKey.String())

	msgChan <- response
}

type OptionsType struct {
	caseInsensitive bool
	wholeWord       bool
	wholeLine       bool
	filenameOnly    bool
	filesWoMatches  bool
}

func isBinary(fileToRead string) (bool, error) {
	data := make([]byte, 256)
	file, err := os.Open(fileToRead)
	if err != nil {
		return false, err
	}
	defer file.Close()
	count, err := file.Read(data)
	if err != nil {
		return false, err
	}
	for i := 0; i < count; i++ {
		if data[i] == 0 {
			return true, nil
		}
	}
	return false, nil
}

func checkFileForPattern(fileToRead string, pattern string, options OptionsType) ([]string, error) {
	matches := make([]string, 0)
	r, err := regexp.Compile(pattern)
	if err != nil {
		return nil, err
	}
	file, err := os.Open(fileToRead)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	fi, err := file.Stat()
	if err != nil {
		return nil, err
	}
	if fi.Size() == 0 {
		return nil, nil
	}

	fileIsBinary, err := isBinary(fileToRead)
	if err != nil {
		return nil, err
	}
	if fileIsBinary {
		log.Printf("%s is binary\n", fileToRead)
		return nil, nil
	}

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var txtlines []string
	for scanner.Scan() {
		txtlines = append(txtlines, scanner.Text())
	}
	if len(txtlines) == 0 {
		log.Printf("%s has no new line control characters.\n", fileToRead)
		return nil, nil
	}
	fileToRead = strings.ReplaceAll(fileToRead, `\\`, `\`)
	numNonMatches := 0
	for lineNum, line := range txtlines {
		if r.MatchString(line) {
			if options.filesWoMatches == false {
				if options.filenameOnly == true {
					match := fmt.Sprintf("%s\n\n", fileToRead)
					matches = append(matches, match)
					break
				}
				var printableLine string
				var sb strings.Builder
				for _, r := range line {
					if int(r) >= 32 && int(r) != 127 {
						if r == '\\' || r == '"' {
							sb.WriteRune('\\')
						}
						sb.WriteRune(r)
					}
				}
				printableLine = sb.String()
				match := fmt.Sprintf("%s: %d:\n %s\n\n", fileToRead, lineNum+1, printableLine)
				matches = append(matches, match)
			}
		} else {
			numNonMatches++
		}
	}
	if options.filesWoMatches == true && numNonMatches == len(txtlines) {
		match := fmt.Sprintf("%s\n\n", fileToRead)
		matches = append(matches, match)
	}
	return matches, nil
}

func walkDir(pattern, dirToWalk string, options OptionsType) (string, error) {
	var matches []string
	err := filepath.Walk(dirToWalk, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			matchesFromFile, err2 := checkFileForPattern(path, pattern, options)
			if err2 != nil {
				log.Printf("Failed opening file: %s", err2)
			} else {
				matches = append(matches, matchesFromFile...)
			}
		}
		return nil
	})

	if err != nil {
		return "", err
	}

	result := strings.Join(matches, "")
	return result, nil
}

func main() {
	// cli()

	var keyFilePath string
	var password string
	var rpcUri string
	var contractAddress string
	var fileInputPath string
	var outputFilePath string
	var claimId int64

	gtk.Init(nil)

	// Create new main window
	win, err := gtk.WindowNew(gtk.WINDOW_TOPLEVEL)
	if err != nil {
		log.Fatal("Unable to create window:", err)
	}
	win.SetTitle("Moonstream signer")
	win.Connect("destroy", func() {
		gtk.MainQuit()
	})

	// Inside box structure
	mainBox, err := gtk.BoxNew(gtk.ORIENTATION_VERTICAL, 10)
	if err != nil {
		log.Fatal("Unable to create mainBox:", err)
	}
	// Create a new label widget to show in the window.
	msgLbl, err := gtk.LabelNew("Generate signatures for claimants")
	if err != nil {
		log.Fatal("Unable to create label:", err)
	}
	mainBox.PackStart(msgLbl, false, false, 10)

	// ROW 1 - Sector with path to claimans and search button
	// ROW 1 - Label
	r1LblBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r1LabelBox:", err)
	}
	r1Lbl, err := gtk.LabelNew("Path to file with claimants")
	if err != nil {
		log.Fatal("Unable to create r1Lbl:", err)
	}
	r1LblBox.PackStart(r1Lbl, false, false, 10)

	// ROW 1 - Input and button
	r1Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r1Box:", err)
	}
	r1PathBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r1PathBox:", err)
	}
	r1PathEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r1PathEnt:", err)
	}
	r1SearchBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r1SearchBtn:", err)
	}
	r1SearchBtn.SetLabel("Search")

	r1SearchBtn.Connect("clicked", func() {
		fileChooserDlg, err := gtk.FileChooserNativeDialogNew("Open", win, gtk.FILE_CHOOSER_ACTION_OPEN, "_Open", "_Cancel")
		if err != nil {
			log.Fatal("Unable to create fileChooserDlg:", err)
		}
		response := fileChooserDlg.NativeDialog.Run()
		if gtk.ResponseType(response) == gtk.RESPONSE_ACCEPT {
			fileChooser := fileChooserDlg
			filename := fileChooser.GetFilename()
			r1PathEnt.SetText(filename)
		} else {
			cancelDlg := gtk.MessageDialogNew(win, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, "%s", "No file was selected")
			cancelDlg.Run()
			cancelDlg.Destroy()
		}
	})

	// ROW 1 - Packaging
	r1PathBox.PackStart(r1PathEnt, true, true, 0)
	r1Box.PackStart(r1PathBox, true, true, 10)
	r1Box.PackStart(r1SearchBtn, false, false, 10)

	mainBox.PackStart(r1LblBox, false, false, 0)
	mainBox.PackStart(r1Box, false, false, 0)

	// ROW 2 - Contract address
	// ROW 2 - Label
	r2Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r2Box:", err)
	}
	r2Lbl, err := gtk.LabelNew("Contract address")
	if err != nil {
		log.Fatal("Unable to create r2Lbl:", err)
	}

	// ROW 2 - Drop-down select menu
	r2MenuWithMnemonic, err := gtk.MenuItemNewWithMnemonic("")
	if err != nil {
		log.Fatal(err)
	}
	r2Menu, err := gtk.MenuNew()
	if err != nil {
		log.Fatal("Could not create r2Menu:", err)
	}
	r2MenuWithMnemonic.SetSubmenu(r2Menu)

	r2MenuItemMainnet, err := gtk.MenuItemNewWithLabel("0x6bc613A25aFe159b70610b64783cA51C9258b92e (Mainnet)")
	if err != nil {
		log.Fatal("Could not create menu r2MenuItemMainnet:", err)
	}

	r2MenuItemMainnet.Connect("activate", func() {
		r2MenuWithMnemonic.SetLabel(r2MenuItemMainnet.GetLabel())
	})
	r2MenuItemMumbai, err := gtk.MenuItemNewWithLabel("0x000000000000000000000000000000000000dead (Mumbai)")
	if err != nil {
		log.Fatal("Could not create menu r2MenuItemMumbai:", err)
	}
	r2MenuItemMumbai.Connect("activate", func() {
		r2MenuWithMnemonic.SetLabel(r2MenuItemMumbai.GetLabel())
	})
	r2Menu.Append(r2MenuItemMainnet)
	r2Menu.Append(r2MenuItemMumbai)

	// TODO(kompotkot): Not sure about this approach
	r2MenuItemMainnet.Activate() // Select by default

	r2MenuBar, err := gtk.MenuBarNew()
	if err != nil {
		log.Fatal(err)
	}
	r2MenuBar.Append(r2MenuWithMnemonic)

	// ROW 2 - Packaging
	r2Box.PackStart(r2Lbl, false, false, 10)
	r2Box.PackStart(r2MenuBar, true, true, 10)

	mainBox.PackStart(r2Box, false, false, 0)

	// ROW 3 - Claim ID
	r3Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r3Box:", err)
	}
	r3Lbl, err := gtk.LabelNew("Claim ID")
	if err != nil {
		log.Fatal("Unable to create r3Lbl:", err)
	}
	r3IdBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r3IdBox:", err)
	}
	r3IdEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r3IdEnt:", err)
	}

	// ROW 3 - Packaging
	r3IdBox.PackStart(r3IdEnt, true, true, 0)

	r3Box.PackStart(r3Lbl, false, false, 10)
	r3Box.PackStart(r3IdBox, true, true, 10)

	mainBox.PackStart(r3Box, false, false, 0)

	// ROW 4 - Sector with path to keyfile
	// ROW 4 - Label
	r4LblBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r4LabelBox:", err)
	}
	r4Lbl, err := gtk.LabelNew("Path to keyfile")
	if err != nil {
		log.Fatal("Unable to create r4Lbl:", err)
	}
	r4LblBox.PackStart(r4Lbl, false, false, 10)

	// ROW 4 - Input and button
	r4Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r4Box:", err)
	}
	r4PathBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r4PathBox:", err)
	}
	r4PathEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r4PathEnt:", err)
	}
	r4SearchBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r4SearchBtn:", err)
	}
	r4SearchBtn.SetLabel("Search")

	r4SearchBtn.Connect("clicked", func() {
		fileChooserDlg, err := gtk.FileChooserNativeDialogNew("Open", win, gtk.FILE_CHOOSER_ACTION_OPEN, "_Open", "_Cancel")
		if err != nil {
			log.Fatal("Unable to create fileChooserDlg:", err)
		}
		response := fileChooserDlg.NativeDialog.Run()
		if gtk.ResponseType(response) == gtk.RESPONSE_ACCEPT {
			fileChooser := fileChooserDlg
			filename := fileChooser.GetFilename()
			r4PathEnt.SetText(filename)
		} else {
			cancelDlg := gtk.MessageDialogNew(win, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, "%s", "No file was selected")
			cancelDlg.Run()
			cancelDlg.Destroy()
		}
	})

	// ROW 4 - Packaging
	r4PathBox.PackStart(r4PathEnt, true, true, 0)
	r4Box.PackStart(r4PathBox, true, true, 10)
	r4Box.PackStart(r4SearchBtn, false, false, 10)

	mainBox.PackStart(r4LblBox, false, false, 0)
	mainBox.PackStart(r4Box, false, false, 0)

	// ROW 5 - Password for keyfile
	r5Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r5Box:", err)
	}
	r5Lbl, err := gtk.LabelNew("Password to keyfile")
	if err != nil {
		log.Fatal("Unable to create r5Lbl:", err)
	}
	r5PasswordBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r5PasswordBox:", err)
	}
	r5PasswordEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r5PasswordEnt:", err)
	}
	r5PasswordEnt.SetVisibility(false)

	// ROW 5 - Packaging
	r5PasswordBox.PackStart(r5PasswordEnt, true, true, 0)

	r5Box.PackStart(r5Lbl, false, false, 10)
	r5Box.PackStart(r5PasswordBox, true, true, 10)

	mainBox.PackStart(r5Box, false, false, 0)

	// ROW 6 - RPC URI
	r6Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r6Box:", err)
	}
	r6Lbl, err := gtk.LabelNew("RPC URI")
	if err != nil {
		log.Fatal("Unable to create r6Lbl:", err)
	}
	r6RpcUriBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r6RpcUriBox:", err)
	}
	r6RpcUriEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r6RpcUriEnt:", err)
	}

	// ROW 6 - Packaging
	r6RpcUriBox.PackStart(r6RpcUriEnt, true, true, 0)

	r6Box.PackStart(r6Lbl, false, false, 10)
	r6Box.PackStart(r6RpcUriBox, true, true, 10)

	mainBox.PackStart(r6Box, false, false, 0)

	// ROW 0 - Generate button
	r0Box, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r0Box:", err)
	}
	r0GenBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r0GenBtn:", err)
	}
	r0GenBtn.SetLabel("Generate")
	r0GenBtn.Connect("clicked", func() {
		workDlg := gtk.MessageDialogNew(win, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, "%s", "Working...")
		go func() {
			glib.IdleAdd(func() {
				workDlg.Show()
			})

			keyFilePath, err = r4PathEnt.GetText()
			if err != nil {
				fmt.Println("Unable to get keyfile path")
			}

			password, err = r5PasswordEnt.GetText()
			if err != nil {
				fmt.Println("Unable to get password")
			}

			rpcUri, err = r6RpcUriEnt.GetText()
			if err != nil {
				fmt.Println("Unable to get rpc uri")
			}

			contractAddressLabel := r2MenuItemMainnet.GetLabel()
			contractAddress = strings.Split(contractAddressLabel, " ")[0]

			fileInputPath, err = r1PathEnt.GetText()
			if err != nil {
				fmt.Println("Unable to get file input path")
			}

			claimIdStr, err := r3IdEnt.GetText()
			if err != nil {
				fmt.Println("Unable to get claim ID")
			}
			claimId, err = strconv.ParseInt(claimIdStr, 10, 64)
			if err != nil {
				fmt.Printf("%d of type %T", claimId, claimId)
			}

			workingDir, err := os.Getwd()
			if err != nil {
				fmt.Println("Unable to get current dir", err)
			}
			outputFilePath = fmt.Sprintf("%s/output", workingDir)

			msgChan := make(chan string)
			go getMsg(msgChan, password, keyFilePath, rpcUri, contractAddress, fileInputPath, outputFilePath, claimId)
			msg := <-msgChan

			glib.IdleAdd(func() {
				fmt.Println(msg)
			})
			glib.IdleAdd(func() {
				workDlg.Destroy()
			})
		}()
	})

	// ROW 0 - Packaging
	r0Box.PackStart(r0GenBtn, true, true, 10)

	mainBox.PackStart(r0Box, false, false, 20)

	// Add the label to the window
	win.Add(mainBox)

	// Set the default window size
	win.SetDefaultSize(800, 400)

	// Recursively show all widgets contained in this window
	win.ShowAll()

	// Begin executing the GTK main loop.  This blocks until
	// gtk.MainQuit() is run
	gtk.Main()
}
