import React, { useEffect, useState } from "react";
import { Box } from "@chakra-ui/react";

interface ConnectionsProps {
  links: Map<string, string[]>;
}

const getPoints = (id: string) => {
  const card = document.getElementById(id);
  if (!card) {
    return;
  }
  const x = card.offsetLeft + card.offsetWidth / 2;

  return {
    top: { x, y: card.offsetTop },
    bottom: { x, y: card.offsetTop + card.offsetHeight },
  };
};

const Connections = ({ links }: ConnectionsProps) => {
  const [connections, setConnections] = useState<React.CSSProperties[]>([]);

  useEffect(() => {
    console.log("Connections useEffect");
    const connections: React.CSSProperties[] = [];

    for (const [key, value] of links.entries()) {
      const source = getPoints(key);
      if (!source) {
        return;
      }
      if (value.length > 1) {
        const borderTop = "dashed 2px white";
        const leftToRight = value
          .map((targetId) => getPoints(targetId)!)
          .sort((a, b) => a.top.x - b.top.x);
        leftToRight.forEach((target, idx) => {
          const height = Math.ceil((target.top.y - source.bottom.y) / 2);
          const middle = source.bottom.y + height;
          if (target.top.x < source.top.x) {
            connections.push({
              top: middle,
              left: target.top.x,
              width:
                Math.min(leftToRight[idx + 1].top.x + 10, source.top.x) -
                target.top.x,
              height: target.top.y - middle + 1,
              borderTop,
              borderLeft: borderTop,
              borderRadius: "10px 0 0 0",
            });
          } else {
            connections.push({
              top: target.top.x === source.top.x ? source.bottom.y : middle,
              left: source.top.x,
              width:
                Math.min(leftToRight[idx].top.x, target.top.x) - source.top.x,
              height:
                target.top.x === source.top.x
                  ? target.top.y - source.bottom.y
                  : target.top.y - middle + 1,
              borderTop,
              borderRight: borderTop,
              borderRadius: "0 10px 0 0",
            });
          }
        });
      } else {
        value.forEach((targetId) => {
          const target = getPoints(targetId);
          if (!target) {
            return;
          }
          const width = Math.abs(target.top.x - source.top.x) / 2;
          const top = source.bottom.y;
          const height = Math.ceil((target.top.y - source.bottom.y) / 2);
          const middle = source.bottom.y + height;
          const borderLeft = "solid 2px white";
          if (target.top.x < source.top.x) {
            connections.push({
              top,
              left: source.top.x - width + 1,
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
              left: source.top.x,
              width,
              height: (target.top.y - top) / 2 + 1,
              borderLeft,
              borderBottom: borderLeft,
              borderRadius: "0 0 0 10px",
            });
            connections.push({
              top: middle - 1,
              left: source.top.x + width,
              width,
              height: target.top.y - middle + 1,
              borderRight: borderLeft,
              borderTop: borderLeft,
              borderRadius: "0 10px 0 0",
            });
          }
        });
      }
    }
    setConnections(connections);
  }, [links]);

  return (
    <>
      {connections.map((box: React.CSSProperties, idx: number) => (
        <Box position="absolute" key={idx} style={box} />
      ))}
    </>
  );
};

export default Connections;
