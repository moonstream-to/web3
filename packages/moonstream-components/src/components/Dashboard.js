import React, { useContext, useEffect, useState } from "react";
import {
  Spinner,
  Flex,
  Heading,
  Stack,
  Text,
  Spacer,
  IconButton,
} from "@chakra-ui/react";
import RangeSelector from "./RangeSelector";
import { BiTrash } from "react-icons/bi";
import SubscriptionReport from "./SubscriptionReport";
import OverlayContext from "../core/providers/OverlayProvider/context";
import { useSubscriptions, useDashboard } from "../core/hooks";
import { v4 } from "uuid";

const HOUR_KEY = "Hourly";
const DAY_KEY = "Daily";
const MINUTE_KEY = "Minutes";
let timeMap = {};
timeMap[DAY_KEY] = "month";
timeMap[HOUR_KEY] = "week";
timeMap[MINUTE_KEY] = "day";

const Dashboard = ({ dashboardId }) => {
  const { toggleAlert } = useContext(OverlayContext);
  const [timeRange, setTimeRange] = useState(timeMap[MINUTE_KEY]);

  const { dashboardCache, dashboardLinksCache, deleteDashboard } =
    useDashboard(dashboardId);

  const { subscriptionsCache } = useSubscriptions();

  useEffect(() => {
    if (typeof window !== "undefined") {
      if (dashboardCache?.data?.data?.resource_data?.name) {
        document.title = dashboardCache?.data?.data?.resource_data?.name;
      } else {
        document.title = `Dashboard`;
      }
    }
  }, [dashboardCache?.data?.data?.resource_data?.name]);

  if (
    dashboardCache.isLoading ||
    dashboardLinksCache.isLoading ||
    subscriptionsCache.isLoading
  )
    return <Spinner />;

  const plotMinW = "250px";
  return (
    <>
      <Flex
        h="100%"
        w="100%"
        m={0}
        px={["10px", "20px", "7%", null]}
        direction="column"
        alignItems="center"
        minH="100vh"
      >
        <Stack direction={["column", "row", null]} w="100%" placeItems="center">
          <Heading as="h1" py={2} fontSize={["md", "xl"]}>
            {dashboardCache.data.data.resource_data.name}
            <IconButton
              icon={<BiTrash />}
              variant="ghost"
              colorScheme="red"
              size="sm"
              onClick={() => toggleAlert(() => deleteDashboard.mutate())}
            />
          </Heading>
          <Spacer />
          <RangeSelector
            initialRange={MINUTE_KEY}
            ranges={Object.keys(timeMap)}
            size={["sm", "md", null]}
            onChange={(e) => {
              setTimeRange(timeMap[e]);
            }}
          />
        </Stack>

        <Flex w="100%" direction="row" flexWrap="wrap-reverse" id="container">
          {Object.keys(dashboardLinksCache.data.data).map((key) => {
            const s3PresignedURLs = dashboardLinksCache.data.data[key];
            const name = subscriptionsCache.data.subscriptions.find(
              (subscription) => subscription.id === key
            ).label;
            return (
              <Flex
                key={v4()}
                flexBasis={plotMinW}
                flexGrow={1}
                minW={plotMinW}
                minH="320px"
                direction="column"
                boxShadow="md"
                m={["1px", 2]}
              >
                <Text
                  w="100%"
                  py={2}
                  bgColor="gray.50"
                  fontWeight="600"
                  textAlign="center"
                >
                  {name}
                </Text>
                <SubscriptionReport
                  timeRange={timeRange}
                  url={s3PresignedURLs[timeRange]}
                  id={v4()}
                  type={v4()}
                  refetchLinks={dashboardLinksCache.refetch}
                />
              </Flex>
            );
          })}
        </Flex>
      </Flex>
    </>
  );
};

export default Dashboard;
