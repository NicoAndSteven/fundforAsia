import { FlowItemGroup } from '@/components/panels/left/flow-item-group';
import { SearchBox } from '@/components/panels/search-box';
import { Accordion } from '@/components/ui/accordion';
import { useTabsContext } from '@/contexts/tabs-context';
import { Flow } from '@/types/flow';
import { FolderOpen } from 'lucide-react';

interface FlowListProps {
  flows: Flow[];
  searchQuery: string;
  isLoading: boolean;
  openGroups: string[];
  filteredFlows: Flow[];
  recentFlows: Flow[];
  templateFlows: Flow[];
  onSearchChange: (query: string) => void;
  onAccordionChange: (value: string[]) => void;
  onLoadFlow: (flow: Flow) => Promise<void>;
  onDeleteFlow: (flow: Flow) => Promise<void>;
  onRefresh: () => Promise<void>;
}

export function FlowList({
  flows,
  searchQuery,
  isLoading,
  openGroups,
  filteredFlows,
  recentFlows,
  templateFlows,
  onSearchChange,
  onAccordionChange,
  onLoadFlow,
  onDeleteFlow,
  onRefresh,
}: FlowListProps) {
  const { tabs, activeTabId } = useTabsContext();

  const getActiveFlowId = (): number | null => {
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    
    if (!activeTab || activeTab.type !== 'flow') {
      return null;
    }
    
    return activeTab.flow?.id || null;
  };

  const activeFlowId = getActiveFlowId();

  return (
    <div className="flex-grow overflow-auto text-primary scrollbar-thin scrollbar-thumb-ramp-grey-700">
      <SearchBox 
        value={searchQuery} 
        onChange={onSearchChange}
        placeholder="搜索流程..."
      />
      
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-muted-foreground text-sm">正在加载流程...</div>
        </div>
      ) : (
        <Accordion 
          type="multiple" 
          className="w-full" 
          value={openGroups} 
          onValueChange={onAccordionChange}
        >
          {recentFlows.length > 0 && (
            <FlowItemGroup
              key="recent-flows"
              title="最近流程"
              flows={recentFlows}
              onLoadFlow={onLoadFlow}
              onDeleteFlow={onDeleteFlow}
              onRefresh={onRefresh}
              currentFlowId={activeFlowId}
            />
          )}
          
          {templateFlows.length > 0 && (
            <FlowItemGroup
              key="templates"
              title="模板"
              flows={templateFlows}
              onLoadFlow={onLoadFlow}
              onDeleteFlow={onDeleteFlow}
              onRefresh={onRefresh}
              currentFlowId={activeFlowId}
            />
          )}
        </Accordion>
      )}

      {!isLoading && filteredFlows.length === 0 && (
        <div className="text-center py-8 text-muted-foreground text-sm">
          {flows.length === 0 ? (
            <div className="space-y-2">
              <FolderOpen size={32} className="mx-auto text-muted-foreground" />
              <div>暂无保存的流程</div>
              <div className="text-xs">创建您的第一个流程开始使用</div>
            </div>
          ) : (
            '没有找到匹配的流程'
          )}
        </div>
      )}
    </div>
  );
}