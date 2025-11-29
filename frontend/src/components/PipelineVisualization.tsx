import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PipelineData } from '@/lib/pipelineParser';
import { StepCard } from './StepCard';
import { ScrollArea } from './ui/scroll-area';

type StepStatus = 'pending' | 'processing' | 'completed' | 'error';

interface PipelineStep {
  id: string;
  title: string;
  description: string;
  details: any;
}

interface PipelineVisualizationProps {
  data: PipelineData | null;
  isRunning: boolean;
  currentStep: number;
  onNodeClick: (nodeData: any) => void;
}

export const PipelineVisualization = ({
  data,
  isRunning,
  currentStep,
  onNodeClick,
}: PipelineVisualizationProps) => {
  const [steps, setSteps] = useState<PipelineStep[]>([]);

  useEffect(() => {
    // Define fixed pipeline steps for real execution
    const pipelineSteps: PipelineStep[] = [
      {
        id: 'server',
        title: 'Start Server',
        description: 'Initialize pipeline server',
        details: { step: 'server' },
      },
      {
        id: 'coordinator',
        title: 'Coordinator Agent',
        description: 'Orchestrating pipeline workflow',
        details: { step: 'coordinator' },
      },
      {
        id: 'ingest',
        title: 'Ingest Agent',
        description: 'Normalizing experiment data',
        details: { step: 'ingest' },
      },
      {
        id: 'diagnosis',
        title: 'Diagnosis Agent',
        description: 'Analyzing metrics and detecting issues',
        details: { step: 'diagnosis' },
      },
      {
        id: 'ml_improvement',
        title: 'ML Improvement Agent',
        description: 'Generating improvement recommendations',
        details: { step: 'ml_improvement' },
      },
      {
        id: 'evaluation',
        title: 'Evaluation Agent',
        description: 'Evaluating current model state',
        details: { step: 'evaluation' },
      },
      {
        id: 'planner',
        title: 'Planner Agent',
        description: 'Creating comprehensive action plan',
        details: { step: 'planner' },
      },
    ];

    setSteps(pipelineSteps);
  }, [data]);

  const getStepStatus = (index: number): StepStatus => {
    if (!isRunning) return 'pending';
    if (currentStep > index) return 'completed';
    if (currentStep === index) return 'processing';
    return 'pending';
  };

  if (!data) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center h-full bg-gradient-to-b from-background to-muted/30"
      >
        <div className="text-center space-y-4 p-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="text-6xl"
          >
            🔍
          </motion.div>
          <h3 className="text-xl font-semibold text-foreground">No Pipeline Detected</h3>
          <p className="text-muted-foreground max-w-md">
            Paste your ML pipeline code in the editor and click "Parse & Visualize" to see the flow
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="h-full w-full bg-gradient-to-b from-background to-muted/20">
      <ScrollArea className="h-full">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="max-w-2xl mx-auto py-8 px-6"
        >
          {/* Pipeline Header */}
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="mb-8 text-center"
          >
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Pipeline Execution Flow
            </h2>
            <p className="text-muted-foreground">
              {isRunning ? 'Processing steps...' : 'Ready to simulate'}
            </p>
          </motion.div>

          {/* Steps */}
          <div className="space-y-6">
            <AnimatePresence mode="wait">
              {steps.map((step, index) => (
                <StepCard
                  key={step.id}
                  number={index + 1}
                  title={step.title}
                  description={step.description}
                  status={getStepStatus(index)}
                  isLast={index === steps.length - 1}
                  onClick={() => onNodeClick(step.details)}
                />
              ))}
            </AnimatePresence>
          </div>

          {/* Completion Message */}
          {isRunning && currentStep >= steps.length && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-8 p-6 bg-green-500/10 border-2 border-green-500/30 rounded-2xl text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
                className="inline-block text-5xl mb-3"
              >
                ✓
              </motion.div>
              <h3 className="text-xl font-semibold text-green-500 mb-1">
                Pipeline Completed
              </h3>
              <p className="text-muted-foreground text-sm">
                All steps executed successfully
              </p>
            </motion.div>
          )}
        </motion.div>
      </ScrollArea>
    </div>
  );
};
