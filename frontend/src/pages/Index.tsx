import { useState, useEffect } from 'react';
import { CodeEditor } from '@/components/CodeEditor';
import { PipelineVisualization } from '@/components/PipelineVisualization';
import { DetailPanel } from '@/components/DetailPanel';
import { PlaybackControls } from '@/components/PlaybackControls';
import { ThemeToggle } from '@/components/ThemeToggle';
import { parsePipelineCode, PipelineData, SAMPLE_CODE } from '@/lib/pipelineParser';
import { APIClient, PipelineStep, PipelineResponse, AgentEvent } from '@/lib/api-client';
import { motion } from 'framer-motion';
import { Workflow } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const [code, setCode] = useState(SAMPLE_CODE);
  const [pipelineData, setPipelineData] = useState<PipelineData | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [failedAgent, setFailedAgent] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [improvedCode, setImprovedCode] = useState<string>('');
  const [pipelineResult, setPipelineResult] = useState<PipelineResponse | null>(null);
  const [stepStatuses, setStepStatuses] = useState<Record<string, 'pending' | 'processing' | 'completed' | 'error'>>({});
  const [realtimeData, setRealtimeData] = useState<{
    overview?: any;
    pipeline_json?: any;
    logs?: any[];
    improved_code?: Array<{
      pipeline_id: string;
      file_path: string;
      original_code: string;
      improved_code: string;
      diff: string;
      annotations: Array<{line: number; type: string; comment: string}>;
      summary: string;
    }>;
  }>({});
  const [improvedFiles, setImprovedFiles] = useState<Array<{
    pipeline_id: string;
    file_path: string;
    original_code: string;
    improved_code: string;
    diff: string;
    annotations: Array<{line: number; type: string; comment: string}>;
    summary: string;
  }>>([]);
  
  const { toast } = useToast();
  const apiClient = new APIClient();

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(initialTheme);
  }, []);

  const handleParse = () => {
    const parsed = parsePipelineCode(code);
    setPipelineData(parsed);
    setLogs([]);
    setCurrentStep(0);
    setIsRunning(false);
    setIsPaused(false);
    addLog('✓ Pipeline parsed successfully');
  };

  const handleClear = () => {
    setCode('');
    setPipelineData(null);
    setLogs([]);
    setCurrentStep(0);
    setIsRunning(false);
    setIsPaused(false);
    setImprovedCode('');
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const runEventDrivenPipeline = async (experimentData: any) => {
    try {
      setIsRunning(true);
      setCurrentStep(0);
      setStepStatuses({});
      setImprovedCode('');
      setPipelineResult(null);
      setFailedAgent(null);
      setRealtimeData({});
      setImprovedFiles([]);
      addLog('🚀 Starting event-driven pipeline execution...');
      
      const stepOrder = ['server', 'coordinator', 'ingest_agent', 'diagnosis_agent', 'ml_improvement_agent', 'eval_agent', 'planner_agent'];
      
      await apiClient.runPipelineEventDriven(
        experimentData,
        (event: AgentEvent) => {
          // Update step status
          setStepStatuses(prev => ({
            ...prev,
            [event.agent]: event.status === 'success' ? 'completed' : 
                          event.status === 'failed' ? 'error' : 'processing'
          }));
          
          // Update current step index only on agent completion
          if (event.status === 'success' || event.status === 'failed') {
            const stepIndex = stepOrder.indexOf(event.agent);
            if (stepIndex >= 0) {
              setCurrentStep(stepIndex + 1);
            }
          }
          
          // Add log with timestamp
          const statusIcon = event.status === 'processing' ? '⏳' : 
                           event.status === 'success' ? '✅' : 
                           event.status === 'failed' ? '❌' : '🔄';
          const time = new Date(event.timestamp).toLocaleTimeString();
          addLog(`[${time}] ${statusIcon} ${event.agent}: ${event.payload?.message || event.status}`);
          
          // Handle agent failure
          if (event.status === 'failed') {
            setFailedAgent(event.agent);
            setIsRunning(false);
            addLog(`❌ Agent ${event.agent} failed: ${event.error}`);
            return;
          }
          
          // Update real-time data from agent payloads
          if (event.payload) {
            // Extract improved files from ML improvement agent
            if (event.agent === 'ml_improvement_agent' && event.status === 'success') {
              if (event.payload.improved_files) {
                setImprovedFiles(event.payload.improved_files);
                setRealtimeData(prev => ({ ...prev, improved_code: event.payload.improved_files }));
                addLog(`📝 Generated ${event.payload.improved_files.length} improved files!`);
                
                // Set legacy improved code to first file for backward compatibility
                if (event.payload.improved_files.length > 0) {
                  setImprovedCode(event.payload.improved_files[0].improved_code);
                }
              } else if (event.payload.improved_code) {
                // Legacy format
                const legacyFile = {
                  pipeline_id: event.payload.run_id || 'unknown',
                  file_path: "models/legacy_model.py",
                  original_code: event.payload.original_code || "# Original code not available",
                  improved_code: event.payload.improved_code,
                  diff: "# Diff will be generated",
                  annotations: [
                    {line: 15, type: "add", comment: "Legacy format improvements"}
                  ],
                  summary: "Legacy improvements applied"
                };
                setImprovedFiles([legacyFile]);
                setRealtimeData(prev => ({ ...prev, improved_code: [legacyFile] }));
                setImprovedCode(event.payload.improved_code);
                addLog('📝 Improved code generated!');
              }
            }
            
            // Update overview data
            if (event.payload.baseline_metrics || event.payload.improved_metrics) {
              setRealtimeData(prev => ({
                ...prev,
                overview: {
                  ...prev.overview,
                  ...event.payload
                }
              }));
            }
          }
        },
        (result: PipelineResponse) => {
          setPipelineResult(result);
          setCurrentStep(stepOrder.length);
          setIsRunning(false);
          setFailedAgent(null);
          
          // Update all real-time data from final result
          if (result.overview) {
            setRealtimeData(prev => ({ ...prev, overview: result.overview }));
          }
          if (result.pipeline_json) {
            setRealtimeData(prev => ({ ...prev, pipeline_json: result.pipeline_json }));
          }
          if (result.improved_code) {
            setRealtimeData(prev => ({ ...prev, improved_code: result.improved_code }));
          }
          
          // Extract improved files from final result
          if (result.improved_code && result.improved_code.length > 0) {
            setImprovedFiles(result.improved_code);
            setImprovedCode(result.improved_code[0].improved_code);
            addLog(`📝 Final improved code: ${result.improved_code.length} files received!`);
          } else if (result.ml_improvement?.improved_files) {
            setImprovedFiles(result.ml_improvement.improved_files);
            if (result.ml_improvement.improved_files.length > 0) {
              setImprovedCode(result.ml_improvement.improved_files[0].improved_code);
            }
            addLog(`📝 Improved files from ML agent: ${result.ml_improvement.improved_files.length} files!`);
          } else if (result.ml_improvement?.improved_code) {
            // Legacy format
            const legacyFile = {
              pipeline_id: result.run_id || 'unknown',
              file_path: "models/legacy_model.py",
              original_code: result.ml_improvement.original_code || "# Original code not available",
              improved_code: result.ml_improvement.improved_code,
              diff: "# Diff will be generated",
              annotations: [{line: 15, type: "add", comment: "Legacy format improvements"}],
              summary: "Legacy improvements applied"
            };
            setImprovedFiles([legacyFile]);
            setImprovedCode(result.ml_improvement.improved_code);
            addLog('📝 Improved code from ML agent received!');
          }
          
          addLog('🎉 Pipeline completed successfully!');
          toast({
            title: 'Pipeline Completed',
            description: 'All agents have finished processing your experiment.',
          });
        },
        (error: string) => {
          setIsRunning(false);
          setFailedAgent('pipeline');
          addLog(`❌ Pipeline failed: ${error}`);
          toast({
            title: 'Pipeline Failed',
            description: error,
            variant: 'destructive',
          });
        }
      );
    } catch (error) {
      setIsRunning(false);
      setFailedAgent('pipeline');
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addLog(`❌ Failed to start pipeline: ${errorMessage}`);
      toast({
        title: 'Failed to Start Pipeline',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const totalSteps = 7; // server, coordinator, ingest, diagnosis, ml_improvement, evaluation, planner

  const handlePlay = () => {
    if (!pipelineData) return;
    
    if (currentStep === 0) {
      // Create sample experiment data for testing
      const sampleExperiment = {
        run_id: `exp_${Date.now()}`,
        model: 'Sample ML Model',
        metrics: {
          accuracy: 0.75,
          loss: 0.45,
          f1_score: 0.72,
          precision: 0.78,
          recall: 0.68
        },
        hyperparameters: {
          learning_rate: 0.001,
          batch_size: 32,
          epochs: 50
        },
        timestamp: new Date().toISOString()
      };
      
      // Run event-driven pipeline
      runEventDrivenPipeline(sampleExperiment);
    } else {
      setIsRunning(true);
      setIsPaused(false);
    }
  };

  const handlePause = () => {
    setIsPaused(true);
    addLog('⏸ Simulation paused');
  };

  const handleStep = () => {
    if (!pipelineData || currentStep >= totalSteps - 1) return;
    
    setCurrentStep(prev => prev + 1);
    setIsRunning(true);
    setIsPaused(true);
  };

  const handleRestart = () => {
    setCurrentStep(0);
    setIsRunning(false);
    setIsPaused(false);
    setLogs([]);
    setFailedAgent(null);
    setRealtimeData({});
    addLog('↺ Pipeline reset');
  };

  const handleRetryAgent = () => {
    if (!failedAgent || !pipelineData) return;
    addLog(`🔄 Retrying ${failedAgent}...`);
    setFailedAgent(null);
    // In a real implementation, this would call a retry endpoint
    // For now, just restart the whole pipeline
    handlePlay();
  };

  const handleSkipAgent = () => {
    if (!failedAgent) return;
    addLog(`⏭️ Skipping ${failedAgent}...`);
    setFailedAgent(null);
    setIsRunning(true);
    // Continue to next step
    setCurrentStep(prev => prev + 1);
  };

  return (
    <div className="flex flex-col h-screen w-full bg-background">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-border bg-card/50 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Workflow className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Pipeline Visualizer</h1>
              <p className="text-xs text-muted-foreground">Automatically detect and visualize ML agent pipelines</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-[400px_1fr_400px] h-full">
          {/* Left: Code Editor */}
          <div className="border-r border-border overflow-hidden">
            <CodeEditor
              value={code}
              onChange={setCode}
              onParse={handleParse}
              onClear={handleClear}
              theme={theme}
            />
          </div>

          {/* Center: Pipeline Visualization */}
          <div className="overflow-hidden">
            <PipelineVisualization
              data={pipelineData}
              isRunning={isRunning && !isPaused}
              currentStep={currentStep}
              onNodeClick={setSelectedNode}
            />
          </div>

          {/* Right: Detail Panel */}
          <div className="overflow-hidden">
            <DetailPanel
              data={pipelineData}
              logs={logs}
              selectedNode={selectedNode}
              improvedCode={improvedCode}
              pipelineResult={pipelineResult}
              realtimeData={realtimeData}
              improvedFiles={improvedFiles}
            />
          </div>
        </div>
      </div>

      {/* Bottom: Playback Controls */}
      {pipelineData && (
        <PlaybackControls
          isRunning={isRunning}
          isPaused={isPaused}
          onPlay={handlePlay}
          onPause={handlePause}
          onRestart={handleRestart}
          canRetry={!!failedAgent}
          onRetry={handleRetryAgent}
          onSkip={handleSkipAgent}
        />
      )}
    </div>
  );
};

export default Index;
