import { useTabsContext } from '@/contexts/tabs-context';
import { cn } from '@/lib/utils';
import { TabService } from '@/services/tab-service';
import { FileText, FolderOpen } from 'lucide-react';
import { useEffect } from 'react';

interface TabContentProps {
  className?: string;
}

export function TabContent({ className }: TabContentProps) {
  const { tabs, activeTabId, openTab } = useTabsContext();

  const activeTab = tabs.find(tab => tab.id === activeTabId);

  // Restore content for tabs that don't have it (from localStorage restoration)
  useEffect(() => {
    if (activeTab && !activeTab.content) {
      try {
        const restoredTab = TabService.restoreTab({
          type: activeTab.type,
          title: activeTab.title,
          flow: activeTab.flow,
          metadata: activeTab.metadata,
        });

        // Update the tab with restored content
        openTab({
          id: activeTab.id,
          type: restoredTab.type,
          title: restoredTab.title,
          content: restoredTab.content,
          flow: restoredTab.flow,
          metadata: restoredTab.metadata,
        });
      } catch (error) {
        console.error('Failed to restore tab content:', error);
      }
    }
  }, [activeTab, openTab]);

  // No tabs at all: show welcome screen
  if (tabs.length === 0) {
    return (
      <div className={cn(
        "h-full w-full flex items-center justify-center bg-background text-muted-foreground",
        className
      )}>
        <div className="text-center space-y-4">
          <FolderOpen size={48} className="mx-auto text-muted-foreground/50" />
          <div>
            <div className="text-xl font-medium mb-2">欢迎使用 AI Hedge Fund</div>
            <div className="text-sm max-w-md">
              从左侧栏创建一个流程 (⌘B) 在标签页中打开，或打开设置 (⌘,) 配置你的偏好。
            </div>
          </div>
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground/70">
            <FileText size={14} />
            <span>流程现在在标签页中打开</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("h-full w-full bg-background overflow-hidden", className)}>
      {tabs.map(tab => (
        <div
          key={tab.id}
          className={cn("h-full w-full", tab.id !== activeTabId && "hidden")}
        >
          {tab.content || (
            <div className="h-full w-full flex items-center justify-center bg-background text-muted-foreground">
              <div className="text-center">
                <div className="text-lg font-medium mb-2">加载中 {tab.title}...</div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
} 