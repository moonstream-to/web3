import React from "react";
import { Box, Spinner, chakra, Container } from "@chakra-ui/react";
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

function FileUpload({ isUploading, columns, ...props }) {
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

  const str = columns ? columns.map((item) => item) : `address,amount`;
  return (
    <Container
      {...props}
      size="md"
      minH="50px"
      className="container"
      alignItems={"center"}
    >
      <Box h={[null, null, "105px"]} {...getRootProps({ style })}>
        {isUploading ? (
          <Spinner colorScheme="blue" speed="1s" size="xl" p="0" m="0" />
        ) : (
          <>
            <input {...getInputProps()} />
            <p>{`Drag 'n' drop some files here, or click to select files`}</p>
            <p>{`We expect csv file in format: "${str}" `}</p>
          </>
        )}
      </Box>
    </Container>
  );
}

export default chakra(FileUpload);
