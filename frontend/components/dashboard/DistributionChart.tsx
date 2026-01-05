'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, Sector } from 'recharts'
import { motion } from 'framer-motion'
import { PieChart as PieChartIcon } from 'lucide-react'
import { useState } from 'react'


const data = [
    { name: '派遣社員', value: 300, color: '#3b82f6' }, // Blue
    { name: '請負社員', value: 150, color: '#f59e0b' }, // Amber
    { name: '待機中', value: 50, color: '#64748b' },   // Slate
]

const COLORS = ['#3b82f6', '#f59e0b', '#64748b']

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white/95 backdrop-blur-sm p-3 rounded-xl shadow-xl border border-slate-100 dark:bg-slate-800/95 dark:border-slate-700">
                <p className="font-semibold text-slate-900 dark:text-white mb-1">
                    {payload[0].name}
                </p>
                <p className="text-sm">
                    <span style={{ color: payload[0].fill }}>●</span> {payload[0].value}名
                </p>
            </div>
        )
    }
    return null
}

const renderActiveShape = (props: any) => {
    const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload, value } = props;

    return (
        <g>
            <text x={cx} y={cy} dy={-10} textAnchor="middle" fill="#1e293b" className="text-2xl font-bold dark:fill-white">
                {(value / 5).toFixed(0)}%
            </text>
            <text x={cx} y={cy} dy={15} textAnchor="middle" fill="#64748b" className="text-xs">
                {payload.name}
            </text>
            <Sector
                cx={cx}
                cy={cy}
                innerRadius={innerRadius}
                outerRadius={outerRadius}
                startAngle={startAngle}
                endAngle={endAngle}
                fill={fill}
            />
            <Sector
                cx={cx}
                cy={cy}
                startAngle={startAngle}
                endAngle={endAngle}
                innerRadius={outerRadius + 6}
                outerRadius={outerRadius + 10}
                fill={fill}
            />
        </g>
    );
};



// Bypass type checking for Pie component due to version mismatch
const PieAny = Pie as any;

export function DistributionChart() {
    const [activeIndex, setActiveIndex] = useState(0);

    const onPieEnter = (_: any, index: number) => {
        setActiveIndex(index);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-6 h-full flex flex-col items-center justify-center relative overflow-hidden"
        >
            <div className="w-full flex items-center justify-between mb-2">
                <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                        社員構成
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                        雇用形態別の割合
                    </p>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 p-2 rounded-lg text-orange-600 dark:text-orange-400">
                    <PieChartIcon size={20} />
                </div>
            </div>

            <div className="h-[280px] w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <PieAny
                            activeIndex={activeIndex}
                            activeShape={renderActiveShape}
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                            onMouseEnter={onPieEnter}
                            stroke="none"
                            cornerRadius={8}
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </PieAny>
                        {/* <Legend 
              verticalAlign="bottom" 
              height={36} 
              iconType="circle"
              wrapperStyle={{ fontSize: '12px' }}
            /> */}
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Custom Legend */}
            <div className="flex justify-center gap-6 w-full text-sm">
                {data.map((item, index) => (
                    <div
                        key={index}
                        className={`flex items-center gap-2 transition-opacity ${index === activeIndex ? 'opacity-100 font-medium' : 'opacity-60'}`}
                        onMouseEnter={() => setActiveIndex(index)}
                    >
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-slate-600 dark:text-slate-300">{item.name}</span>
                    </div>
                ))}
            </div>

        </motion.div>
    )
}

