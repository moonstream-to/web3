import React, { useContext, useRef, useEffect } from "react";
import { useForm } from "react-hook-form";
import {
  Flex,
  Button,
  Textarea,
  FormControl,
  FormErrorMessage,
  InputGroup,
  Input,
  VStack,
  FormLabel,
} from "@chakra-ui/react";
// import { CloseIcon } from "@chakra-ui/icons";

const NewDrop = () => {
  const {
    handleSubmit,
    formState: { errors },
    register,
  } = useForm();
  const inputRef = useRef();

  useEffect(() => {
    inputRef.current.focus();
  }, [inputRef]);

  const handleNewDrop = (arggs) => {
    console.log("args:", arggs);
  };

  const { ref, ...rest } = register("dropName", {
    required: "Name is required",
  });

  const [description, setDescripton] = React.useState("");
  const handleDescriptionChange = (e) => {
    setDescripton(e.target.value);
  };
  console.log("new drop form render");

  return (
    <Flex
      className="NewDrop"
      minH="100vh"
      w="100%"
      maxW="1337px"
      placeContent={"center"}
      // bgColor="white.100"
      p={2}
    >
      <form onSubmit={handleSubmit(handleNewDrop)}>
        <VStack py={2} width="100%">
          <FormControl isInvalid={errors.dropName} isRequired>
            <FormLabel textColor="gray.300" htmlFor="terminusAddress">
              Title
            </FormLabel>
            <InputGroup>
              <Input
                pl={2}
                colorScheme={"blue"}
                variant="flushed"
                border="none"
                // width="60%"
                placeholder="Drop name"
                name="dropName"
                {...rest}
                ref={(e) => {
                  ref(e);
                  inputRef.current = e; // you can still assign to ref
                }}
              />
            </InputGroup>
            <FormErrorMessage color="red.400" pl="1" h="24px">
              {errors.dropName && errors.dropName.message}
            </FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={errors.description} isRequired>
            <FormLabel textColor="gray.300" htmlFor="terminusAddress">
              Description
            </FormLabel>
            <InputGroup>
              <Textarea
                borderRadius={"md"}
                {...register("description", {
                  required: "This field is required",
                })}
                px={2}
                bgColor={"blue.200"}
                border="none"
                // width="60%"
                colorScheme={"blue"}
                variant="flushed"
                value={description}
                onChange={handleDescriptionChange}
                placeholder="Describe your drop in few words"
                name="description"
              />
            </InputGroup>
            <FormErrorMessage color="red.400" pl="1" h="24px">
              {errors.description && errors.description.message}
            </FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={errors.Deadline}>
            <FormLabel textColor="gray.300" htmlFor="terminusAddress">
              Block Deadline
            </FormLabel>
            <InputGroup>
              <Input
                pl={2}
                colorScheme={"blue"}
                variant="flushed"
                border="none"
                // width="60%"
                placeholder="Claim block deadline"
                name="Deadline"
                {...register("Deadline")}
              />
            </InputGroup>
            <FormErrorMessage color="red.400" pl="1">
              {errors.dropName && errors.dropName.message}
            </FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={errors.terminusAddress}>
            <FormLabel textColor="gray.300" htmlFor="terminusAddress">
              Terminus address
            </FormLabel>
            <InputGroup>
              <Input
                pl={2}
                colorScheme={"blue"}
                variant="flushed"
                border="none"
                // width="60%"
                placeholder="Claim block deadline"
                name="terminusAddress"
                {...register("terminusAddress")}
              />
            </InputGroup>
            <FormErrorMessage color="red.400" pl="1" h="24px">
              {errors.dropName && errors.dropName.message}
            </FormErrorMessage>
          </FormControl>
          <Button type="submit">Submit!</Button>
          {/* <Button onClick={() => toggleSelf(false)} icon={<CloseIcon />} /> */}
        </VStack>
      </form>
    </Flex>
  );
};
export default NewDrop;
