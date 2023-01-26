import React, { useEffect, useState } from "react";
import { Box } from "@chakra-ui/react";

interface ConnectionsProps {
  links: Map<string, string>;
  futureStages: { sources: string[]; targets: string[] }[];
  width: number;
  offsets?: { top: { x: number; y: number }; bottom: { x: number; y: number } };
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

  useEffect(() => {
    const connections: React.CSSProperties[] = [];

    futureStages.forEach(({ sources, targets }) => {
      const sortedSources = sources
        .map((targetId) => getPoints(targetId)!)
        .sort((a, b) => a.top.x - b.top.x);
      const sortedTargets = targets
        .map((targetId) => getPoints(targetId)!)
        .sort((a, b) => a.top.x - b.top.x);
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
      box.width = right - left + 1;
      box.top = left === leftSource ? sortedSources[0].bottom.y : middle;
      box.height = middle - sortedSources[0].bottom.y;
      if (leftSource <= leftTarget) {
        if (leftSource < leftTarget) {
          box.borderBottomLeftRadius = 10;
          box.borderBottomRightRadius = 10;
        } else {
          box.borderTop = "none";
        }
        box.borderTop = "none";
        sortedTargets.forEach(({ top }) => {
          connections.push({
            left: top.x,
            width: 2,
            top: middle,
            height: top.y - middle,
            borderLeft: box.border,
          });
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
        box.borderBottom = "none";

        sortedSources.forEach(({ bottom }) => {
          connections.push({
            left: bottom.x,
            width: 2,
            top: bottom.y,
            height: middle - bottom.y,
            borderLeft: box.border,
          });
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
      }
      connections.push(box);
    });

    for (const [sourceId, targetId] of links.entries()) {
      const source = getPoints(sourceId);
      const target = getPoints(targetId);
      if (!source || !target) {
        return;
      }

      const width = Math.abs(target.top.x - source.bottom.x) / 2;
      const top = source.bottom.y;
      const height = Math.ceil((target.top.y - source.bottom.y) / 2);
      const middle = source.bottom.y + height;
      const borderLeft = "solid 2px white";
      if (target.top.x < source.bottom.x) {
        connections.push({
          top,
          left: source.bottom.x - width + 1,
          width,
          height: height + 1,
          borderRight: borderLeft,
          borderBottom: borderLeft,
          borderRadius: "0 0 10px 0",
        });
        connections.push({
          top: top + height - 1,
          left: target.top.x,
          width: width + 1,
          height: target.top.y - top - height + 1,
          borderLeft,
          borderTop: borderLeft,
          borderRadius: "10px 0 0 0",
        });
      } else {
        connections.push({
          top,
          left: source.bottom.x,
          width,
          height: (target.top.y - top) / 2 + 1,
          borderLeft,
          borderBottom: borderLeft,
          borderRadius: "0 0 0 10px",
        });
        connections.push({
          top: middle - 1,
          left: source.bottom.x + width,
          width,
          height: target.top.y - middle + 1,
          borderRight: borderLeft,
          borderTop: borderLeft,
          borderRadius: "0 10px 0 0",
        });
      }
    }
    setConnections(connections);
  }, [links, futureStages, width, getPoints]);

  return (
    <>
      {connections.map((box: React.CSSProperties, idx: number) => (
        <Box position="absolute" key={idx} style={box} />
      ))}
    </>
  );
};

export default Connections;
