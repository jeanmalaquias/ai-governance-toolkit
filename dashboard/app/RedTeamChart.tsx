"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Row = { category: string; withstood: number };

export default function RedTeamChart({ data }: { data: Row[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 16, right: 24, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="category" />
        <YAxis domain={[0, 1]} ticks={[0, 1]} />
        <Tooltip />
        <Bar dataKey="withstood">
          {data.map((row) => (
            <Cell
              key={row.category}
              fill={row.withstood ? "#0a7d28" : "#b00020"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
