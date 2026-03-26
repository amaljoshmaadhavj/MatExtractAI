'use client';

import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

interface DataVisualizationProps {
  data: DataPoint[];
  type?: 'bar' | 'line';
  title?: string;
  xAxisKey?: string;
  yAxisKey?: string;
  height?: number;
  showLegend?: boolean;
}

export function DataVisualization({
  data,
  type = 'bar',
  title,
  xAxisKey = 'name',
  yAxisKey = 'value',
  height = 300,
  showLegend = true,
}: DataVisualizationProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center glass-effect rounded-lg">
        <p className="text-foreground/60">No data available</p>
      </div>
    );
  }

  const chartConfig = {
    margin: { top: 5, right: 30, left: 0, bottom: 5 },
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold mb-4 text-foreground">
          {title}
        </h3>
      )}
      <div className="glass-effect p-6 rounded-lg overflow-x-auto">
        <ResponsiveContainer width="100%" height={height}>
          {type === 'bar' ? (
            <BarChart data={data} {...chartConfig}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey={xAxisKey} stroke="var(--color-foreground)" opacity={0.7} />
              <YAxis stroke="var(--color-foreground)" opacity={0.7} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.5rem',
                  color: 'var(--color-foreground)',
                }}
                cursor={{ fill: 'var(--color-primary)', opacity: 0.1 }}
              />
              {showLegend && <Legend />}
              <Bar dataKey={yAxisKey} fill="var(--color-primary)" opacity={0.8} radius={[8, 8, 0, 0]} />
            </BarChart>
          ) : (
            <LineChart data={data} {...chartConfig}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey={xAxisKey} stroke="var(--color-foreground)" opacity={0.7} />
              <YAxis stroke="var(--color-foreground)" opacity={0.7} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.5rem',
                  color: 'var(--color-foreground)',
                }}
                cursor={{ fill: 'var(--color-primary)', opacity: 0.1 }}
              />
              {showLegend && <Legend />}
              <Line
                type="monotone"
                dataKey={yAxisKey}
                stroke="var(--color-primary)"
                dot={{ fill: 'var(--color-primary)', r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
