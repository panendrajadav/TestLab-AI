import { motion } from 'framer-motion';
import { CheckCircle, Loader2, Circle, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

type StepStatus = 'pending' | 'processing' | 'completed' | 'error';

interface StepCardProps {
  number: number;
  title: string;
  description: string;
  status: StepStatus;
  isLast?: boolean;
  onClick?: () => void;
}

export const StepCard = ({ 
  number, 
  title, 
  description, 
  status, 
  isLast = false,
  onClick 
}: StepCardProps) => {
  const statusConfig = {
    pending: {
      icon: Circle,
      iconColor: 'text-muted-foreground',
      cardBg: 'bg-card/50',
      borderColor: 'border-border/50',
      textColor: 'text-muted-foreground',
      showPulse: false,
    },
    processing: {
      icon: Loader2,
      iconColor: 'text-primary',
      cardBg: 'bg-card',
      borderColor: 'border-primary',
      textColor: 'text-foreground',
      showPulse: true,
    },
    completed: {
      icon: CheckCircle,
      iconColor: 'text-green-500',
      cardBg: 'bg-card/80',
      borderColor: 'border-green-500/30',
      textColor: 'text-foreground',
      showPulse: false,
    },
    error: {
      icon: CheckCircle,
      iconColor: 'text-destructive',
      cardBg: 'bg-card/80',
      borderColor: 'border-destructive/30',
      textColor: 'text-foreground',
      showPulse: false,
    },
  };

  const config = statusConfig[status];
  const StatusIcon = config.icon;
  const isExpanded = status === 'processing';

  return (
    <div className="relative">
      {/* Timeline connector */}
      {!isLast && (
        <motion.div
          className={cn(
            'absolute left-6 top-16 w-0.5 h-12 -ml-px',
            status === 'completed' ? 'bg-green-500' : 'bg-border'
          )}
          initial={{ scaleY: 0 }}
          animate={{ scaleY: status === 'completed' ? 1 : 0.3 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          style={{ transformOrigin: 'top' }}
        />
      )}

      {/* Step Card */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: number * 0.1 }}
        whileHover={onClick ? { scale: 1.02, y: -2 } : {}}
        onClick={onClick}
        className={cn(
          'relative rounded-2xl border-2 p-5 transition-all duration-300',
          config.cardBg,
          config.borderColor,
          onClick && 'cursor-pointer',
          isExpanded && 'shadow-lg shadow-primary/20',
          'backdrop-blur-sm'
        )}
      >
        {/* Pulse animation for processing step */}
        {config.showPulse && (
          <motion.div
            className="absolute inset-0 rounded-2xl border-2 border-primary"
            animate={{ scale: [1, 1.05, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}

        <div className="flex items-start gap-4">
          {/* Step Icon/Number */}
          <motion.div
            className={cn(
              'flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full',
              status === 'completed' && 'bg-green-500/10',
              status === 'processing' && 'bg-primary/10',
              status === 'pending' && 'bg-muted/30'
            )}
            animate={
              status === 'processing'
                ? { scale: [1, 1.1, 1] }
                : { scale: 1 }
            }
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <StatusIcon
              className={cn(
                'h-6 w-6',
                config.iconColor,
                status === 'processing' && 'animate-spin'
              )}
            />
          </motion.div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h3
                className={cn(
                  'font-semibold text-lg',
                  config.textColor,
                  isExpanded && 'text-foreground'
                )}
              >
                {title}
              </h3>
              {onClick && (
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              )}
            </div>

            <motion.p
              className={cn(
                'text-sm mt-1',
                status === 'pending' ? 'text-muted-foreground/70' : 'text-muted-foreground'
              )}
              initial={{ opacity: 0 }}
              animate={{ opacity: isExpanded ? 1 : 0.7 }}
            >
              {description}
            </motion.p>

            {/* Progress bar for processing */}
            {status === 'processing' && (
              <motion.div
                className="mt-3 h-1 bg-muted rounded-full overflow-hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <motion.div
                  className="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                />
              </motion.div>
            )}
          </div>
        </div>

        {/* Completion indicator */}
        {status === 'completed' && (
          <motion.div
            className="absolute -right-2 -top-2 bg-green-500 rounded-full p-1"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          >
            <CheckCircle className="h-5 w-5 text-white" />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};
