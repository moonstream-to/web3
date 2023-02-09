import React, { useEffect, useState } from "react";
import { Box } from "@chakra-ui/react";

interface ConnectionsProps {
  links: { source: string; target: string }[];
  futureStages: { sources: string[]; targets: string[] }[];
  width: number;
  offsets?: EntryPoints;
}

interface Point {
  x: number;
  y: number;
}

interface EntryPoints {
  top: Point;
  bottom: Point;
}

const Connections = ({
  links,
  futureStages,
  width,
  offsets = { top: { x: 0, y: 0 }, bottom: { x: 0, y: 0 } },
}: ConnectionsProps) => {
  const [connections, setConnections] = useState<React.CSSProperties[]>([]);

  const getPoints = (id: string) => {
    const card = document.getElementById(id);
    if (!card) {
      return;
    }
    const top = {
      x:
        card.offsetLeft +
        card.offsetWidth / 2 +
        card.offsetWidth * offsets.top.x,
      y: card.offsetTop + card.offsetHeight * offsets.top.y,
    };
    const bottom = {
      x:
        card.offsetLeft +
        card.offsetWidth / 2 +
        card.offsetWidth * offsets.bottom.x,
      y:
        card.offsetTop +
        card.offsetHeight +
        card.offsetHeight * offsets.bottom.y,
    };
    return {
      top,
      bottom,
    };
  };

  const oneToOneConnection = (
    source: EntryPoints,
    target: EntryPoints,

    style: string
  ) => {
    if (!source || !target) {
      return [];
    }
    const connections: React.CSSProperties[] = [];
    const width = Math.abs(target.top.x - source.bottom.x) / 2;
    const top = source.bottom.y + 1;
    const height = Math.ceil((target.top.y - source.bottom.y) / 2);
    const middle = source.bottom.y + height;
    const borderLeft = style;
    if (target.top.x < source.bottom.x) {
      connections.push({
        top,
        left: source.bottom.x - width + 1,
        width,
        height: middle - top,
        borderRight: borderLeft,
        borderBottom: borderLeft,
        borderRadius: "0 0 10px 0",
      });
      connections.push({
        top: middle - 2,
        left: target.top.x,
        width: width + 1,
        height: middle - top,
        borderLeft,
        borderTop: borderLeft,
        borderRadius: "10px 0 0 0",
      });
    } else {
      connections.push({
        top,
        left: source.bottom.x,
        width,
        height: middle - top,
        borderLeft,
        borderBottom: borderLeft,
        borderRadius: "0 0 0 10px",
      });
      connections.push({
        top: middle - 2,
        left: source.bottom.x + width,
        width,
        height: middle - top,
        borderRight: borderLeft,
        borderTop: borderLeft,
        borderRadius: "0 10px 0 0",
      });
    }
    return connections;
  };

  useEffect(() => {
    const connections: React.CSSProperties[] = [];
    futureStages.forEach(({ sources, targets }) => {
      const sortedSources = sources
        .map((sourceId) => getPoints(sourceId)!)
        .sort((a, b) => a.top.x - b.top.x);
      const sortedTargets = targets
        .map((targetId) => getPoints(targetId)!)
        .sort((a, b) => a.top.x - b.top.x);
      if (sources.length === 1 && targets.length === 1) {
        connections.push(
          ...oneToOneConnection(
            sortedSources[0],
            sortedTargets[0],
            "dashed 2px white"
          )
        );
      } else {
        const rightSource = sortedSources[sortedSources.length - 1].bottom.x;
        const rightTarget = sortedTargets[sortedTargets.length - 1].top.x;
        const leftSource = sortedSources[0].bottom.x;
        const leftTarget = sortedTargets[0].top.x;
        const middle =
          sortedSources[0].bottom.y +
          (sortedTargets[0].top.y - sortedSources[0].bottom.y) / 2;
        const right = Math.max(rightSource, rightTarget);
        const left = Math.min(leftSource, leftTarget);

        const box: React.CSSProperties = { border: "dashed 2px white" };
        box.left = left;
        box.width = right - left + 2;
        box.top = left === leftSource ? sortedSources[0].bottom.y : middle;
        box.height = middle - sortedSources[0].bottom.y;

        if (leftSource <= leftTarget) {
          box.borderStyle = "none dashed dashed dashed";
          if (leftSource < leftTarget) {
            box.borderBottomLeftRadius = 10;
            box.borderBottomRightRadius = 10;
          }
          if (rightSource < rightTarget) {
            connections.push(
              ...oneToOneConnection(
                sortedSources[0],
                sortedTargets[sortedTargets.length - 1],
                "dashed 2px white"
              )
            );
          } else {
            connections.push({ ...box });
          }

          sortedTargets.forEach(({ top }) => {
            if (rightSource >= rightTarget || top.x !== rightTarget) {
              connections.push({
                left: top.x,
                width: 2,
                top: middle,
                height: top.y - middle,
                borderLeft: box.border,
              });
            }
          });
          for (let i = 1; i < sortedSources.length - 1; i += 1) {
            connections.push({
              left: sortedSources[i].bottom.x,
              width: 2,
              top: sortedSources[0].bottom.y,
              height: middle - sortedSources[0].bottom.y,
              borderLeft: box.border,
            });
          }
        }
        if (leftSource > leftTarget) {
          box.borderTopLeftRadius = 10;
          box.borderTopRightRadius = 10;
          box.borderStyle = "dashed dashed none dashed";
          if (rightSource > rightTarget) {
            connections.push(
              ...oneToOneConnection(
                sortedSources[sortedSources.length - 1],
                sortedTargets[0],
                "dashed 2px white"
              )
            );
          } else {
            connections.push({ ...box });
          }

          sortedSources.forEach(({ bottom }) => {
            if (rightSource <= rightTarget || bottom.x !== rightSource) {
              connections.push({
                left: bottom.x,
                width: 2,
                top: bottom.y,
                height: middle - bottom.y,
                borderLeft: box.border,
              });
            }
          });
          for (let i = 1; i < sortedTargets.length - 1; i += 1) {
            connections.push({
              left: sortedTargets[i].top.x,
              width: 2,
              top: middle,
              height: sortedTargets[0].top.y - middle,
              borderLeft: box.border,
            });
          }
          if (rightSource > rightTarget) {
            connections.push({
              left: sortedTargets[sortedTargets.length - 1].top.x,
              width: 2,
              top: middle,
              height: sortedTargets[0].top.y - middle,
              borderLeft: box.border,
            });
          }
        }
      }
    });

    for (const link of links) {
      const source = getPoints(link.source);
      const target = getPoints(link.target);

      if (!source || !target) {
        return;
      }
      connections.push(
        ...oneToOneConnection(source, target, "solid 2px white")
      );
    }
    setConnections(connections);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [links, futureStages, width]);

  return (
    <>
      {connections.map((box: React.CSSProperties, idx: number) => (
        <Box position="absolute" key={idx} style={box} />
      ))}
    </>
  );
};

export default Connections;
