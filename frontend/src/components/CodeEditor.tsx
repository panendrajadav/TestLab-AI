import { Editor } from '@monaco-editor/react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { Play, Trash2 } from 'lucide-react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onParse: () => void;
  onClear: () => void;
  theme: 'light' | 'dark';
}

export const CodeEditor = ({ value, onChange, onParse, onClear, theme }: CodeEditorProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col h-full"
    >
      <div className="flex items-center justify-between p-4 border-b border-border bg-card">
        <h2 className="text-lg font-semibold text-card-foreground">Code Input</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onClear}
            className="gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Clear
          </Button>
          <Button
            onClick={onParse}
            size="sm"
            className="gap-2"
          >
            <Play className="h-4 w-4" />
            Parse & Visualize
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          defaultLanguage="python"
          theme={theme === 'dark' ? 'vs-dark' : 'light'}
          value={value}
          onChange={(value) => onChange(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            padding: { top: 16, bottom: 16 },
          }}
        />
      </div>
    </motion.div>
  );
};
