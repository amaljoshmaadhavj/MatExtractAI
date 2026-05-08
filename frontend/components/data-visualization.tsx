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
  showLegend = false,
}: DataVisualizationProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center border border-border border-dashed rounded-xl bg-secondary/5">
        <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">No spectral data available</p>
      </div>
    );
  }

  const chartConfig = {
    margin: { top: 10, right: 10, left: -20, bottom: 0 },
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground mb-6">
          {title}
        </h3>
      )}
      <div className="w-full">
        <ResponsiveContainer width="100%" height={height}>
          {type === 'bar' ? (
            <BarChart data={data} {...chartConfig}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis 
                dataKey={xAxisKey} 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={10} 
                fontWeight={600}
                tickLine={false}
                axisLine={false}
                dy={10}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={10} 
                fontWeight={600}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.75rem',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                }}
                cursor={{ fill: 'hsl(var(--primary))', opacity: 0.05 }}
              />
              {showLegend && <Legend />}
              <Bar 
                dataKey={yAxisKey} 
                fill="hsl(var(--primary))" 
                radius={[4, 4, 0, 0]} 
                barSize={32}
              />
            </BarChart>
          ) : (
            <LineChart data={data} {...chartConfig}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis 
                dataKey={xAxisKey} 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={10} 
                fontWeight={600}
                tickLine={false}
                axisLine={false}
                dy={10}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={10} 
                fontWeight={600}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.75rem',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                }}
              />
              {showLegend && <Legend />}
              <Line
                type="monotone"
                dataKey={yAxisKey}
                stroke="hsl(var(--primary))"
                dot={{ fill: 'hsl(var(--primary))', r: 3, strokeWidth: 0 }}
                activeDot={{ r: 5, strokeWidth: 0 }}
                strokeWidth={2.5}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

