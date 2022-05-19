import React from "react";
import { Box, Center, Spinner, chakra, Container } from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";

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

function FileUpload({ isUploading, ...props }) {
  console.log("Render file upload");
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
    <Container
      size="md"
      minH="50px"
      className="container"
      alignItems={"center"}
      {...props}
    >
      {isUploading ? (
        <Box {...getRootProps({ style })}>
          <Spinner colorScheme="blue" speed="1s" size="md" pt="5px" pb="5px" />
        </Box>
      ) : (
        <Box {...getRootProps({ style })}>
          <input {...getInputProps()} />
          <p>{`Drag 'n' drop some files here, or click to select files`}</p>
          <p>{`We expect csv file in format: "address,amount" `}</p>
        </Box>
      )}
    </Container>
  );
}

export default chakra(FileUpload);
