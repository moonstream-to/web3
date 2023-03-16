package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/gotk3/gotk3/glib"
	"github.com/gotk3/gotk3/gtk"
)

func getMsg(msgChan chan string, fileInputPath string, dropperContract DropperContract, claimId int64, keyFilePath, privateKey, password, rpcUri, fileOutputPath string) {
	client, err := InitializeNetworkClient(rpcUri)
	if err != nil {
		msgChan <- fmt.Sprintf("%v", err)
	}

	err = dropperContract.InitializeContractInstance(client)
	if err != nil {
		msgChan <- fmt.Sprintf("%v", err)
	}

	fileInput, err := ParseInput(fileInputPath, false)
	if err != nil {
		msgChan <- fmt.Sprintf("%v", err)
	}

	privateContainer, err := initializeSigner(password, keyFilePath, privateKey)
	if err != nil {
		msgChan <- fmt.Sprintf("%v", err)
	}

	var claimants []Claimant
	for _, input := range fileInput {
		chm, err := dropperContract.claimMessageHash(claimId, input.Address, input.ClaimBlockDeadline, input.Amount)
		if err != nil {
			msgChan <- fmt.Sprintf("%v", err)
		}
		sig, err := privateContainer.sign(chm)
		if err != nil {
			msgChan <- fmt.Sprintf("%v", err)
		}
		claimants = append(claimants, Claimant{
			ClaimantAddress:    input.Address,
			Amount:             input.Amount,
			Signature:          sig,
			ClaimBlockDeadline: input.ClaimBlockDeadline,
			ClaimId:            claimId,
		})
	}

	_, err = ProcessOutput(claimants, fileOutputPath, "csv")
	if err != nil {
		msgChan <- fmt.Sprintf("%v", err)
	}

	msgChan <- fmt.Sprintf("Signed by: %s and output saved at: %s\n\n", privateContainer.publicKey.String(), fileOutputPath)
}

func ui() {
	var workingDir string
	workingDir, err := os.Getwd()
	if err != nil {
		log.Printf("Unable to get working directory, %v", err)
	}

	dropperContracts := InitializeDropperContracts()

	var fileInputPath string
	var claimId int64
	var keyFilePath string
	var privateKey string
	var password string
	var rpcUri string
	var fileOutputPath string

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

	mainBox, err := gtk.BoxNew(gtk.ORIENTATION_VERTICAL, 10)
	if err != nil {
		log.Fatal("Unable to create mainBox:", err)
	}

	// ROW 1 - Path to claimans and search button
	r1LblBox, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r1LabelBox:", err)
	}
	r1LblBox.SetMarginTop(15)
	r1Lbl, err := gtk.LabelNew("Path to CSV file with list of claimants")
	if err != nil {
		log.Fatal("Unable to create r1Lbl:", err)
	}

	// ROW 1 - Input and button
	r1Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r1Box:", err)
	}
	r1InputPathEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r1InputPathEnt:", err)
	}
	r1InputPathEnt.SetPlaceholderText("string")
	if MOONSTREAM_DROPPER_CLAIMANTS_INPUT != "" {
		r1InputPathEnt.SetText(MOONSTREAM_DROPPER_CLAIMANTS_INPUT)
	}
	r1SearchBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r1SearchBtn:", err)
	}
	r1SearchBtn.SetLabel("Search")
	r1SearchBtn.Connect("clicked", func() {
		fileChooserDlg, err := gtk.FileChooserNativeDialogNew("Select", win, gtk.FILE_CHOOSER_ACTION_OPEN, "_Select", "_Cancel")
		if err != nil {
			log.Printf("Unable to create fileChooserDlg %v", err)
			return
		}
		response := fileChooserDlg.NativeDialog.Run()
		if gtk.ResponseType(response) == gtk.RESPONSE_ACCEPT {
			fileChooser := fileChooserDlg
			filename := fileChooser.GetFilename()
			r1InputPathEnt.SetText(filename)
		}
	})

	// ROW 1 - Packaging
	r1LblBox.PackStart(r1Lbl, false, false, 10)

	r1Box.PackStart(r1InputPathEnt, true, true, 10)
	r1Box.PackStart(r1SearchBtn, false, false, 10)

	mainBox.PackStart(r1LblBox, false, false, 0)
	mainBox.PackStart(r1Box, false, false, 0)

	// ROW 2 - Contract address and claim ID
	r2Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r2Box:", err)
	}
	r2Lbl, err := gtk.LabelNew("Contract address")
	if err != nil {
		log.Fatal("Unable to create r2Lbl:", err)
	}
	r2Lbl.SetWidthChars(18)
	r2Lbl.SetXAlign(0)

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

	for n, dc := range dropperContracts {
		r2MenuItem, err := gtk.MenuItemNewWithLabel(fmt.Sprintf("%s - %s", dc.Address.String(), n))
		if err != nil {
			log.Fatal("Could not create menu r2MenuItem:", err)
		}
		r2MenuItem.Connect("activate", func() {
			r2MenuWithMnemonic.SetLabel(r2MenuItem.GetLabel())
		})
		r2Menu.Append(r2MenuItem)

		if n == "polygon" {
			// TODO(kompotkot): Not sure about this approach
			r2MenuItem.Activate() // Select by default
		}
	}

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
	r3Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r3Box:", err)
	}
	r3Lbl, err := gtk.LabelNew("Claim ID")
	if err != nil {
		log.Fatal("Unable to create r3Lbl:", err)
	}
	r3Lbl.SetWidthChars(18)
	r3Lbl.SetXAlign(0)
	r3ClaimIdEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r3ClaimIdEnt:", err)
	}
	r3ClaimIdEnt.SetPlaceholderText("uuid")
	if MOONSTREAM_DROPPER_CLAIM_ID != "" {
		r3ClaimIdEnt.SetText(MOONSTREAM_DROPPER_CLAIM_ID)
	}

	// ROW 3 - Packaging
	r3Box.PackStart(r3Lbl, false, false, 10)
	r3Box.PackStart(r3ClaimIdEnt, true, true, 10)

	mainBox.PackStart(r3Box, false, false, 0)

	// ROW 4 - Separator
	r4Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r4Box:", err)
	}
	r4Box.SetMarginTop(10)
	r4Box.SetMarginBottom(5)
	r4Sep, err := gtk.SeparatorNew(gtk.ORIENTATION_HORIZONTAL)
	if err != nil {
		log.Fatal("Unable to create r4Sep:", err)
	}
	r4Box.PackStart(r4Sep, true, true, 10)
	mainBox.PackStart(r4Box, false, false, 0)

	// ROW 5 and 6
	r6Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r6Box:", err)
	}

	// ROW 5 - Path to keyfile
	r5LblBox, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r5LblBox:", err)
	}
	r5Lbl, err := gtk.LabelNew("Path to keyfile")
	if err != nil {
		log.Fatal("Unable to create r5Lbl:", err)
	}

	// ROW 5 - Input and button
	r5Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r5Box:", err)
	}
	r5KeyfilePathEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r5KeyfilePathEnt:", err)
	}
	r5KeyfilePathEnt.SetPlaceholderText("string")
	if KEYFILE_PATH != "" {
		r5KeyfilePathEnt.SetText(KEYFILE_PATH)
	}

	// If keyfile specified then deactivate private key input
	r5KeyfilePathEnt.Connect("notify", func() {
		r5KeyfilePathEntContent, _ := r5KeyfilePathEnt.GetText()
		if r5KeyfilePathEntContent != "" {
			r6Box.SetSensitive(false)
		} else {
			r6Box.SetSensitive(true)
		}
	})

	r5SearchBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r5SearchBtn:", err)
	}
	r5SearchBtn.SetLabel("Search")
	r5SearchBtn.Connect("clicked", func() {
		fileChooserDlg, err := gtk.FileChooserNativeDialogNew("Select", win, gtk.FILE_CHOOSER_ACTION_OPEN, "_Select", "_Cancel")
		if err != nil {
			log.Fatal("Unable to create fileChooserDlg:", err)
		}
		response := fileChooserDlg.NativeDialog.Run()
		if gtk.ResponseType(response) == gtk.RESPONSE_ACCEPT {
			fileChooser := fileChooserDlg
			filename := fileChooser.GetFilename()
			r5KeyfilePathEnt.SetText(filename)
		}
	})

	// ROW 5 - Packaging
	r5LblBox.PackStart(r5Lbl, false, false, 10)

	r5Box.PackStart(r5KeyfilePathEnt, true, true, 10)
	r5Box.PackStart(r5SearchBtn, false, false, 10)

	mainBox.PackStart(r5LblBox, false, false, 0)
	mainBox.PackStart(r5Box, false, false, 0)

	// ROW 6 - Private key
	r6Lbl, err := gtk.LabelNew("Private key")
	if err != nil {
		log.Fatal("Unable to create r6Lbl:", err)
	}
	r6Lbl.SetWidthChars(18)
	r6Lbl.SetXAlign(0)
	r6PrivateKeyEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to creatGetTexte r9PrivateKeyEnt:", err)
	}
	r6PrivateKeyEnt.SetPlaceholderText("string")
	r6PrivateKeyEnt.SetVisibility(false)
	if PRIVATE_KEY != "" {
		r5KeyfilePathEntContent, _ := r5KeyfilePathEnt.GetText()
		if r5KeyfilePathEntContent == "" {
			r6PrivateKeyEnt.SetText(PRIVATE_KEY)
		}
	}

	// If private key specified then deactivate keyfile input
	r6PrivateKeyEnt.Connect("notify", func() {
		r6PrivateKeyEntContent, _ := r6PrivateKeyEnt.GetText()
		if r6PrivateKeyEntContent != "" {
			r5Box.SetSensitive(false)
		} else {
			r5Box.SetSensitive(true)
		}
	})

	// ROW 6 - Packaging
	r6Box.PackStart(r6Lbl, false, false, 10)
	r6Box.PackStart(r6PrivateKeyEnt, true, true, 10)

	mainBox.PackStart(r6Box, false, false, 0)

	// ROW 7 - Password for key
	r7Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r7Box:", err)
	}
	r7Lbl, err := gtk.LabelNew("Password to keyfile")
	if err != nil {
		log.Fatal("Unable to create r7Lbl:", err)
	}
	r7Lbl.SetWidthChars(18)
	r7Lbl.SetXAlign(0)
	r7PasswordEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r7PasswordEnt:", err)
	}
	r7PasswordEnt.SetPlaceholderText("string")
	r7PasswordEnt.SetVisibility(false)
	if KEYFILE_PASSWORD != "" {
		r7PasswordEnt.SetText(KEYFILE_PASSWORD)
	}

	// ROW 7 - Packaging
	r7Box.PackStart(r7Lbl, false, false, 10)
	r7Box.PackStart(r7PasswordEnt, true, true, 10)

	mainBox.PackStart(r7Box, false, false, 0)

	// ROW 8 - Separator
	r8Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r8Box:", err)
	}
	r8Box.SetMarginTop(10)
	r8Box.SetMarginBottom(5)
	r8Sep, err := gtk.SeparatorNew(gtk.ORIENTATION_HORIZONTAL)
	if err != nil {
		log.Fatal("Unable to create r4Sep:", err)
	}
	r8Box.PackStart(r8Sep, true, true, 10)
	mainBox.PackStart(r8Box, false, false, 0)

	// ROW 9 - RPC URI
	r9Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r9Box:", err)
	}
	r9Lbl, err := gtk.LabelNew("JSON RPC URI")
	if err != nil {
		log.Fatal("Unable to create r9Lbl:", err)
	}
	r9Lbl.SetWidthChars(18)
	r9Lbl.SetXAlign(0)
	r9RpcUriEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r9RpcUriEnt:", err)
	}
	r9RpcUriEnt.SetPlaceholderText("string")
	if JSON_RPC_URI != "" {
		r9RpcUriEnt.SetText(JSON_RPC_URI)
	}

	// ROW 9 - Packaging
	r9Box.PackStart(r9Lbl, false, false, 10)
	r9Box.PackStart(r9RpcUriEnt, true, true, 10)

	mainBox.PackStart(r9Box, false, false, 0)

	// ROW 10 - Path to output and search button
	r10LblBox, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r10LblBox:", err)
	}
	r10LblBox.SetMarginTop(15)
	r10Lbl, err := gtk.LabelNew("Path to output CSV file")
	if err != nil {
		log.Fatal("Unable to create r10Lbl:", err)
	}

	// ROW 10 - Output and button
	r10Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r10Box:", err)
	}
	r10OutputPathEnt, err := gtk.EntryNew()
	if err != nil {
		log.Fatal("Unable to create r10OutputPathEnt:", err)
	}
	r10OutputPathEnt.SetPlaceholderText("string")
	if MOONSTREAM_DROPPER_CLAIMANTS_OUTPUT != "" {
		r10OutputPathEnt.SetText(MOONSTREAM_DROPPER_CLAIMANTS_OUTPUT)
	} else {
		r10OutputPathEnt.SetText(fmt.Sprintf("%s/output.csv", workingDir))
	}
	r10SearchBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r10SearchBtn:", err)
	}
	r10SearchBtn.SetLabel("Search")
	r10SearchBtn.Connect("clicked", func() {
		fileChooserDlg, err := gtk.FileChooserNativeDialogNew("Select", win, gtk.FILE_CHOOSER_ACTION_OPEN, "_Select", "_Cancel")
		if err != nil {
			log.Printf("Unable to create fileChooserDlg %v", err)
			return
		}
		response := fileChooserDlg.NativeDialog.Run()
		if gtk.ResponseType(response) == gtk.RESPONSE_ACCEPT {
			fileChooser := fileChooserDlg
			filename := fileChooser.GetFilename()
			r10OutputPathEnt.SetText(filename)
		}
	})

	// ROW 10 - Packaging
	r10LblBox.PackStart(r10Lbl, false, false, 10)

	r10Box.PackStart(r10OutputPathEnt, true, true, 10)
	r10Box.PackStart(r10SearchBtn, false, false, 10)

	mainBox.PackStart(r10LblBox, false, false, 0)
	mainBox.PackStart(r10Box, false, false, 0)

	// ROW 0 - Generate and clear button
	r0Box, err := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	if err != nil {
		log.Fatal("Unable to create r0Box:", err)
	}
	r0GenBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r0GenBtn:", err)
	}
	r0GenBtn.SetLabel("Generate")
	r0GenBtn.Connect("clicked", func() {
		workDlg := gtk.MessageDialogNew(win, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, "%s", "Generating...")
		go func() {
			glib.IdleAdd(func() {
				workDlg.Show()
			})

			fileInputPath, err = r1InputPathEnt.GetText()
			if err != nil {
				log.Printf("Unable to read input file path %v", err)
			}

			contractAddressRaw := r2MenuWithMnemonic.GetLabel()
			contractAddress := strings.Split(contractAddressRaw, " - ")[1]
			dropperContract := dropperContracts[contractAddress]

			claimIdStr, err := r3ClaimIdEnt.GetText()
			if err != nil {
				log.Printf("Unable to read claim ID %v", err)
			}
			claimId, err = strconv.ParseInt(claimIdStr, 10, 64)
			if err != nil {
				fmt.Printf("%d of type %T\n", claimId, claimId)
			}

			keyFilePath, err = r5KeyfilePathEnt.GetText()
			if err != nil {
				fmt.Println("Unable to read keyfile path")
			}
			privateKey, err = r6PrivateKeyEnt.GetText()
			if err != nil {
				fmt.Println("Unable to read private key")
			}
			password, err = r7PasswordEnt.GetText()
			if err != nil {
				fmt.Println("Unable to read password")
			}

			rpcUri, err = r9RpcUriEnt.GetText()
			if err != nil {
				fmt.Println("Unable to read JSON RPC URI")
			}

			fileOutputPath, err = r10OutputPathEnt.GetText()
			if err != nil {
				log.Printf("Unable to read file output path %v", err)
			}

			msgChan := make(chan string)
			go getMsg(msgChan, fileInputPath, dropperContract, claimId, keyFilePath, privateKey, password, rpcUri, fileOutputPath)
			msg := <-msgChan

			glib.IdleAdd(func() {
				log.Printf("Generation report: %s", msg)
			})
			glib.IdleAdd(func() {
				workDlg.Destroy()
			})
		}()
	})
	r0ClrBtn, err := gtk.ButtonNew()
	if err != nil {
		log.Fatal("Unable to create r0ClrBtn:", err)
	}
	r0ClrBtn.SetLabel("Clear")
	r0ClrBtn.Connect("clicked", func() {
		r1InputPathEnt.SetText("")
		r3ClaimIdEnt.SetText("")
		r5KeyfilePathEnt.SetText("")
		r6PrivateKeyEnt.SetText("")
		r7PasswordEnt.SetText("")
		r9RpcUriEnt.SetText("")
		r10OutputPathEnt.SetText("")
	})

	// ROW 0 - Packaging
	r0Box.PackStart(r0GenBtn, true, true, 10)
	r0Box.PackStart(r0ClrBtn, false, false, 10)

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
