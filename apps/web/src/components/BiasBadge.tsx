import React from 'react';

interface BiasBadgeProps {
  bias: 'left' | 'center' | 'right';
  size?: 'sm' | 'md' | 'lg';
}

const biasConfig = {
  left: {
    label: 'Left',
    color: 'bg-bias-left',
    textColor: 'text-bias-left',
  },
  center: {
    label: 'Center',
    color: 'bg-bias-center',
    textColor: 'text-bias-center',
  },
  right: {
    label: 'Right',
    color: 'bg-bias-right',
    textColor: 'text-bias-right',
  },
};

export default function BiasBadge({ bias, size = 'md' }: BiasBadgeProps) {
  const config = biasConfig[bias];
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  return (
    <span
      className={`inline-flex items-center ${config.color} ${sizeClasses[size]} text-white rounded-full font-medium`}
    >
      {config.label}
    </span>
  );
}
