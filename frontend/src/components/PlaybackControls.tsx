import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { Play, Pause, RotateCcw } from 'lucide-react';

interface PlaybackControlsProps {
  isRunning: boolean;
  isPaused: boolean;
  onPlay: () => void;
  onPause: () => void;
  onRestart: () => void;
  canRetry?: boolean;
  onRetry?: () => void;
  onSkip?: () => void;
}

export const PlaybackControls = ({
  isRunning,
  isPaused,
  onPlay,
  onPause,
  onRestart,
  canRetry = false,
  onRetry,
  onSkip,
}: PlaybackControlsProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border-t border-border px-6 py-4"
    >
      <div className="flex items-center justify-between gap-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          {!isRunning || isPaused ? (
            <Button onClick={onPlay} size="sm" className="gap-2">
              <Play className="h-4 w-4" />
              {isRunning && isPaused ? 'Resume' : 'Run Pipeline'}
            </Button>
          ) : (
            <Button onClick={onPause} size="sm" variant="secondary" className="gap-2">
              <Pause className="h-4 w-4" />
              Pause
            </Button>
          )}
          
          <Button onClick={onRestart} size="sm" variant="outline" className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Restart
          </Button>
          
          {canRetry && onRetry && (
            <Button onClick={onRetry} size="sm" variant="destructive" className="gap-2">
              Retry Agent
            </Button>
          )}
          
          {canRetry && onSkip && (
            <Button onClick={onSkip} size="sm" variant="outline" className="gap-2">
              Skip Agent
            </Button>
          )}
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            Event-driven pipeline • Real-time updates
          </span>
        </div>
      </div>
    </motion.div>
  );
};
