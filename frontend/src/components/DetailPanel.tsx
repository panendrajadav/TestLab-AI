import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Download, Copy, CheckCircle } from 'lucide-react';
import { PipelineData } from '@/lib/pipelineParser';
import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';

interface DetailPanelProps {
  data: PipelineData | null;
  logs: string[];
  selectedNode: any;
  improvedCode?: string;
  pipelineResult?: any;
  realtimeData?: {
    overview?: any;
    pipeline_json?: any;
    logs?: any[];
    improved_code?: any[];
  };
  improvedFiles?: Array<{
    pipeline_id: string;
    file_path: string;
    original_code: string;
    improved_code: string;
    diff: string;
    annotations: Array<{line: number; type: string; comment: string}>;
    summary: string;
  }>;
}

export const DetailPanel = ({ data, logs, selectedNode, improvedCode = '', pipelineResult, realtimeData = {}, improvedFiles = [] }: DetailPanelProps) => {
  const [copied, setCopied] = useState(false);
  const [codeCopied, setCodeCopied] = useState(false);
  const { toast } = useToast();

  const handleCopyJSON = () => {
    if (!data) return;
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Pipeline JSON copied to clipboard',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pipeline-data.json';
    a.click();
    URL.revokeObjectURL(url);
    toast({
      title: 'Downloaded!',
      description: 'Pipeline JSON saved to file',
    });
  };

  const handleCopyCode = () => {
    if (!improvedCode) return;
    navigator.clipboard.writeText(improvedCode);
    setCodeCopied(true);
    toast({
      title: 'Copied!',
      description: 'Improved code copied to clipboard',
    });
    setTimeout(() => setCodeCopied(false), 2000);
  };

  const handleDownloadCode = () => {
    if (!improvedCode) return;
    const blob = new Blob([improvedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'improved-code.py';
    a.click();
    URL.revokeObjectURL(url);
    toast({
      title: 'Downloaded!',
      description: 'Improved code saved to file',
    });
  };

  if (!data) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center justify-center h-full bg-card border-l border-border"
      >
        <div className="text-center p-8">
          <p className="text-muted-foreground">
            Parse code to view pipeline details
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col h-full bg-card border-l border-border"
    >
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-card-foreground">Pipeline Details</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyJSON}
            className="gap-2"
          >
            {copied ? (
              <CheckCircle className="h-4 w-4 text-success" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
            Copy JSON
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadJSON}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="json">JSON</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="improved-code" className={improvedCode ? '' : 'opacity-50'}>Improved Code</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full p-4">
            {(realtimeData.overview || pipelineResult?.overview) ? (
              <div className="space-y-6">
                {/* Model Overview */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">{(realtimeData.overview || pipelineResult?.overview)?.model_name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{(realtimeData.overview || pipelineResult?.overview)?.summary}</p>
                </div>

                {/* Metrics Comparison */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-muted/50 border border-border">
                    <h4 className="font-medium text-sm mb-3 text-muted-foreground uppercase tracking-wide">Baseline Metrics</h4>
                    <div className="space-y-2">
                      {Object.entries((realtimeData.overview || pipelineResult?.overview)?.baseline_metrics || {}).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-sm capitalize">{key.replace('_', ' ')}</span>
                          <span className="text-sm font-mono">{typeof value === 'number' ? value.toFixed(3) : value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                    <h4 className="font-medium text-sm mb-3 text-green-700 dark:text-green-300 uppercase tracking-wide">Improved Metrics</h4>
                    <div className="space-y-2">
                      {Object.entries((realtimeData.overview || pipelineResult?.overview)?.improved_metrics || {}).map(([key, value]) => {
                        const baseline = (realtimeData.overview || pipelineResult?.overview)?.baseline_metrics?.[key];
                        const improvement = typeof value === 'number' && typeof baseline === 'number' 
                          ? ((value - baseline) / baseline * 100).toFixed(1) 
                          : null;
                        
                        return (
                          <div key={key} className="flex justify-between items-center">
                            <span className="text-sm capitalize">{key.replace('_', ' ')}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-mono">{typeof value === 'number' ? value.toFixed(3) : value}</span>
                              {improvement && (
                                <span className={`text-xs px-1.5 py-0.5 rounded ${
                                  parseFloat(improvement) > 0 ? 'bg-green-500/20 text-green-700 dark:text-green-300' : 
                                  parseFloat(improvement) < 0 ? 'bg-red-500/20 text-red-700 dark:text-red-300' : 
                                  'bg-gray-500/20 text-gray-700 dark:text-gray-300'
                                }`}>
                                  {parseFloat(improvement) > 0 ? '+' : ''}{improvement}%
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Pipeline Structure */}
                {data && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide mb-3">
                      Pipeline Structure
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 rounded-lg bg-muted/50 border border-border">
                        <div className="font-medium text-sm mb-2">Agents ({data.agents?.length || 0})</div>
                        <div className="text-xs text-muted-foreground">
                          {data.agents?.map(agent => agent.name.replace('_agent', '')).join(', ') || 'No agents detected'}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-muted/50 border border-border">
                        <div className="font-medium text-sm mb-2">Entrypoints</div>
                        <div className="text-xs text-muted-foreground">
                          {data.entrypoints?.map(entry => entry.name).join(', ') || 'API Server'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {/* Fallback to original structure if no pipeline result */}
                {data && (
                  <>
                    {/* Entrypoints */}
                    <div>
                      <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide mb-3">
                        Entrypoints
                      </h3>
                      <div className="space-y-2">
                        {data.entrypoints.map((entry, idx) => (
                          <div key={idx} className="p-3 rounded-lg bg-muted/50 border border-border">
                            <div className="font-medium text-sm">{entry.name}</div>
                            <div className="text-xs text-muted-foreground mt-1">Host: {entry.host}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Agents */}
                    <div>
                      <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide mb-3">
                        Agents ({data.agents.length})
                      </h3>
                      <div className="space-y-2">
                        {data.agents.map((agent, idx) => (
                          <div key={idx} className="p-3 rounded-lg bg-muted/50 border border-border">
                            <div className="font-medium text-sm capitalize">
                              {agent.name.replace('_agent', '').replace('_', ' ')}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">{agent.file}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </ScrollArea>
        </TabsContent>

        <TabsContent value="json" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full p-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Pipeline JSON Structure</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const jsonData = realtimeData.pipeline_json || pipelineResult?.pipeline_json || data;
                    navigator.clipboard.writeText(JSON.stringify(jsonData, null, 2));
                    toast({ title: 'Copied!', description: 'Pipeline JSON copied to clipboard' });
                  }}
                  className="gap-2"
                >
                  <Copy className="h-4 w-4" />
                  Copy JSON
                </Button>
              </div>
              <pre className="text-xs font-mono bg-muted/50 p-4 rounded-lg overflow-x-auto border border-border">
                {JSON.stringify(realtimeData.pipeline_json || pipelineResult?.pipeline_json || data, null, 2)}
              </pre>
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="logs" className="flex-1 overflow-hidden mt-0">
          <ScrollArea className="h-full p-4">
            <div className="space-y-1 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="text-muted-foreground text-center py-8">
                  No logs yet. Start pipeline to see real-time events.
                </div>
              ) : (
                logs.map((log, idx) => {
                  // Color-code log levels
                  const getLogColor = (logText: string) => {
                    if (logText.includes('✅') || logText.includes('🎉')) return 'text-green-600 dark:text-green-400';
                    if (logText.includes('❌') || logText.includes('💥')) return 'text-red-600 dark:text-red-400';
                    if (logText.includes('⏳') || logText.includes('🔄')) return 'text-yellow-600 dark:text-yellow-400';
                    if (logText.includes('📝') || logText.includes('📊')) return 'text-blue-600 dark:text-blue-400';
                    return 'text-foreground/80';
                  };
                  
                  return (
                    <div key={idx} className={`${getLogColor(log)} leading-relaxed`}>
                      {log}
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="improved-code" className="flex-1 overflow-hidden mt-0 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="text-sm text-muted-foreground">
              {(improvedFiles.length > 0 || realtimeData.improved_code?.length > 0 || improvedCode) && (
                <span>✨ Generated by ML Improvement Agent ({improvedFiles.length || realtimeData.improved_code?.length || 1} files)</span>
              )}
            </div>
          </div>
          <ScrollArea className="flex-1 p-4">
            {(improvedFiles.length > 0 || realtimeData.improved_code?.length > 0 || improvedCode) ? (
              <div className="space-y-6">
                {/* Render each improved file */}
                {(improvedFiles.length > 0 ? improvedFiles : realtimeData.improved_code || []).map((file, fileIdx) => (
                  <div key={`${file.pipeline_id || 'unknown'}-${file.file_path || fileIdx}`} className="border border-border rounded-lg p-4 space-y-4">
                    {/* File Header */}
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-1">File: {file.file_path}</h4>
                      <p className="text-sm text-blue-600 dark:text-blue-400">
                        {file.summary || "Enhanced ML pipeline with improvements based on diagnosis results"}
                      </p>
                    </div>
                    
                    {/* Key Improvements */}
                    {file.annotations && file.annotations.length > 0 && (
                      <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <h4 className="font-medium text-green-700 dark:text-green-300 mb-2">Key Improvements Applied</h4>
                        <ul className="space-y-1 text-sm text-green-600 dark:text-green-400">
                          {file.annotations.map((annotation, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-xs bg-green-500/20 px-1.5 py-0.5 rounded font-mono">L{annotation.line}</span>
                              <span>{annotation.comment}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(file.improved_code);
                          setCodeCopied(true);
                          toast({ title: 'Copied!', description: `Code for ${file.file_path} copied to clipboard` });
                          setTimeout(() => setCodeCopied(false), 2000);
                        }}
                        className="gap-2"
                      >
                        {codeCopied ? <CheckCircle className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const fileName = file.file_path.split('/').pop() || 'improved-code.py';
                          const blob = new Blob([file.improved_code], { type: 'text/plain' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = fileName;
                          a.click();
                          URL.revokeObjectURL(url);
                          toast({ title: 'Downloaded!', description: `${fileName} saved to file` });
                        }}
                        className="gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Download
                      </Button>
                    </div>
                    
                    {/* Diff View */}
                    {file.diff && file.diff !== "# Diff will be generated" && (
                      <div>
                        <h4 className="font-medium text-sm mb-2">Code Changes (Diff)</h4>
                        <pre className="text-xs font-mono bg-muted/50 p-4 rounded-lg overflow-x-auto border border-border whitespace-pre-wrap">
                          <code>{file.diff}</code>
                        </pre>
                      </div>
                    )}
                    
                    {/* Improved Code */}
                    <div>
                      <h4 className="font-medium text-sm mb-2">Complete Improved Code</h4>
                      <pre className="text-xs font-mono bg-muted/50 p-4 rounded-lg overflow-x-auto border border-border whitespace-pre-wrap break-words">
                        <code className="language-python">{file.improved_code}</code>
                      </pre>
                    </div>
                  </div>
                ))}
                
                {/* Fallback for legacy single improved code */}
                {improvedFiles.length === 0 && !realtimeData.improved_code?.length && improvedCode && (
                  <div className="border border-border rounded-lg p-4">
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg mb-4">
                      <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-1">File: Legacy Format</h4>
                      <p className="text-sm text-blue-600 dark:text-blue-400">Legacy improved code format</p>
                    </div>
                    <pre className="text-xs font-mono bg-muted/50 p-4 rounded-lg overflow-x-auto border border-border whitespace-pre-wrap break-words">
                      <code className="language-python">{improvedCode}</code>
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-muted-foreground text-center py-8">
                <div className="text-4xl mb-4">🔧</div>
                <h3 className="font-medium mb-2">Generating improved code...</h3>
                <p className="text-sm">ML Improvement Agent is analyzing your pipeline and generating optimized code</p>
              </div>
            )}
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
};
