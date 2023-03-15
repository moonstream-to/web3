import React from "react";
// install (please make sure versions match peerDependencies)
// yarn add @nivo/core @nivo/line
import { ResponsiveLine } from "@nivo/line";
import { Period } from "../core/types/DashboardTypes";

// make sure parent container have a defined height when using
// responsive component, otherwise height will be 0 and
// no chart will be rendered.
// website examples showcase many properties,
// you'll often use just a few of them.

const getDataFormat = (period: Period) => {
  if (period == Period.Month) return "%Y-%m-%d";
  else return "%Y-%m-%d %H";
};

const getPrintFormat = (period: Period) => {
  if (period == Period.Week) return "%b %d";
  if (period == Period.Month) return "%b %d";
  else return "%b %d %H:00";
};

const getTickValues = (period: Period) => {
  if (period == Period.Week) return "every 1 day";
  if (period == Period.Month) return "every 7 day";
  else return "every 6 hour";
};

const LineChart = ({ data, period }: { data: any; period: Period }) => (
  <ResponsiveLine
    data={data}
    margin={{ top: 50, right: 110, bottom: 30, left: 60 }}
    xScale={{
      type: "time",
      format: getDataFormat(period),
      useUTC: false,
      precision: "hour",
    }}
    xFormat="time:%Y-%m-%d"
    yScale={{
      type: "linear",
      min: "auto",
      max: "auto",
      stacked: false,
      reverse: false,
    }}
    yFormat=" >-.0f"
    axisTop={null}
    axisRight={null}
    axisBottom={{
      format: getPrintFormat(period),
      tickValues: getTickValues(period),
      tickSize: 0,
      tickPadding: 10,
    }}
    axisLeft={{
      tickSize: 0,
      tickPadding: 10,
      tickValues: 4,
    }}
    pointSize={10}
    pointColor={{ theme: "background" }}
    pointBorderWidth={2}
    pointBorderColor={{ from: "serieColor" }}
    pointLabelYOffset={-12}
    useMesh={true}
    curve="natural"
    colors={{ scheme: "pink_yellowGreen" }}
    lineWidth={3}
    enablePoints={false}
    enableGridX={false}
    enableGridY={false}
    theme={{
      textColor: "#FFFFFF",
      background: "transparent",
      annotations: {
        text: {
          fontSize: 13,
          fill: "#333333",
          outlineWidth: 2,
          outlineColor: "#ffffff",
        },
      },
      tooltip: {
        container: {
          background: "#ffffff",
          color: "#333333",
          fontSize: 12,
        },
        basic: {},
        chip: {},
        table: {},
        tableCell: {},
        tableCellValue: {},
      },
    }}
    legends={[]}
  />
);

export default LineChart;
