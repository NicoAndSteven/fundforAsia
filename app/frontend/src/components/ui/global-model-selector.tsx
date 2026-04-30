import { useEffect, useState } from 'react';
import { useNodeContext } from '@/contexts/node-context';
import { getDefaultModel, getModels, LanguageModel } from '@/data/models';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export function GlobalModelSelector() {
  const { globalDefaultModel, setGlobalDefaultModel } = useNodeContext();
  const [models, setModels] = useState<LanguageModel[]>([]);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const fetched = await getModels();
        setModels(fetched.filter(m => m.model_name.trim() !== ''));

        // Auto-set global default on first load if not already set
        if (!globalDefaultModel) {
          const defaultModel = await getDefaultModel();
          if (defaultModel) {
            setGlobalDefaultModel(defaultModel);
          }
        }
      } catch {
        // Keep empty
      }
    };
    loadModels();
    // Only run on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-muted-foreground whitespace-nowrap hidden sm:inline">模型:</span>
      <Select
        value={globalDefaultModel?.model_name || ''}
        onValueChange={(value) => {
          const selected = models.find(m => m.model_name === value) || null;
          setGlobalDefaultModel(selected);
        }}
      >
        <SelectTrigger className="h-7 text-xs w-[130px] sm:w-[160px] border-ramp-grey-700">
          <SelectValue placeholder="全局默认" />
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={model.model_name} value={model.model_name} className="text-xs">
              {model.display_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
