import { Box, Container } from "@chakra-ui/react";
import React, { useContext } from "react";
import { useDropzone } from "react-dropzone";
import Papa from "papaparse";
import useClaimAdmin from "../core/hooks/useClaimAdmin";
import { targetChain } from "../core/providers/Web3Provider";
import Web3Context from "../core/providers/Web3Provider/context";

const baseStyle = {
  flex: 1,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  padding: "20px",
  borderWidth: "4px",
  borderRadius: "29px",
  borderColor: "#eeeeee",
  borderStyle: "dashed",
  backgroundColor: "#fafafa",
  color: "#bdbdbd",
  outline: "none",
  transition: "border .24s ease-in-out",
};

const focusedStyle = {
  borderColor: "#219aa3",
};

const acceptStyle = {
  borderColor: "#00e676",
};

const rejectStyle = {
  borderColor: "#ff1744",
};

//var csv is the CSV file with headers
function csvJSON(csv) {
  console.log("csvJSON", csv);
  var lines = csv.split("\n");

  var result = [];

  // NOTE: If your columns contain commas in their values, you'll need
  // to deal with those before doing the next step
  // (you might convert them to &&& or something, then covert them back later)
  // jsfiddle showing the issue https://jsfiddle.net/
  var headers = lines[0].split(",");

  for (var i = 1; i < lines.length; i++) {
    var obj = {};
    var currentline = lines[i].split(",");

    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = currentline[j];
    }

    result.push(obj);
  }

  //return result; //JavaScript object
  return JSON.stringify(result); //JSON
}

function Basic(props) {
  const web3Ctx = useContext(Web3Context);

  const { uploadFile } = useClaimAdmin({
    targetChain: targetChain,
    ctx: web3Ctx,
  });


  const { getRootProps, getInputProps, isFocused, isDragAccept, isDragReject } =
    useDropzone({ accept: ".csv", onDrop: props.onDrop });

  const style = React.useMemo(
    () => ({
      ...baseStyle,
      ...(isFocused ? focusedStyle : {}),
      ...(isDragAccept ? acceptStyle : {}),
      ...(isDragReject ? rejectStyle : {}),
    }),
    [isFocused, isDragAccept, isDragReject]
  );

  return (
    <Container size="md" minH="50px" className="container">
      <Box {...getRootProps({ style })}>
        <input {...getInputProps()} />
        <p>Drag 'n' drop some files here, or click to select files</p>
        <p>We expect csv file in format: "address, amount" </p>
      </Box>
    </Container>
  );
}

export default Basic;
