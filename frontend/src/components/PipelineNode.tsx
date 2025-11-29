import { Handle, Position } from 'reactflow';
import { motion } from 'framer-motion';
import { CheckCircle, Loader2, AlertCircle, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

type NodeStatus = 'idle' | 'running' | 'success' | 'error';

interface PipelineNodeProps {
  data: {
    label: string;
    sublabel?: string;
    status: NodeStatus;
    details?: any;
  };
}

export const PipelineNode = ({ data }: PipelineNodeProps) => {
  const { label, sublabel, status } = data;

  const statusConfig = {
    idle: {
      icon: Circle,
      color: 'text-node-idle',
      bg: 'bg-node-idle/10',
      border: 'border-node-idle/30',
      glow: false,
    },
    running: {
      icon: Loader2,
      color: 'text-node-running',
      bg: 'bg-node-running/10',
      border: 'border-node-running',
      glow: true,
    },
    success: {
      icon: CheckCircle,
      color: 'text-node-success',
      bg: 'bg-node-success/10',
      border: 'border-node-success',
      glow: false,
    },
    error: {
      icon: AlertCircle,
      color: 'text-node-error',
      bg: 'bg-node-error/10',
      border: 'border-node-error',
      glow: false,
    },
  };

  const config = statusConfig[status];
  const StatusIcon = config.icon;

  return (
    <>
      <Handle type="target" position={Position.Top} className="!bg-primary" />
      
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        whileHover={{ scale: 1.05, y: -4 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'px-6 py-4 rounded-xl border-2 bg-card shadow-lg cursor-pointer min-w-[200px]',
          'transition-all duration-300',
          config.border,
          config.bg,
          config.glow && 'node-glow'
        )}
      >
        <div className="flex items-start gap-3">
          <StatusIcon
            className={cn(
              'h-5 w-5 flex-shrink-0 mt-0.5',
              config.color,
              status === 'running' && 'animate-spin'
            )}
          />
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-card-foreground capitalize">
              {label}
            </div>
            {sublabel && (
              <div className="text-xs text-muted-foreground mt-1 font-mono truncate">
                {sublabel}
              </div>
            )}
          </div>
        </div>
      </motion.div>

      <Handle type="source" position={Position.Bottom} className="!bg-primary" />
    </>
  );
};
