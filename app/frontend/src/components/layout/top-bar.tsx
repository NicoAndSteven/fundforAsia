import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { BarChart3, PanelBottom, PanelLeft, PanelRight, Settings } from 'lucide-react';
import { QuickAnalysis } from '@/components/quick-analysis';
import { GlobalModelSelector } from '@/components/ui/global-model-selector';

interface TopBarProps {
  isLeftCollapsed: boolean;
  isRightCollapsed: boolean;
  isBottomCollapsed: boolean;
  onToggleLeft: () => void;
  onToggleRight: () => void;
  onToggleBottom: () => void;
  onSettingsClick: () => void;
  onOpenMarketDashboard?: () => void;
}

export function TopBar({
  isLeftCollapsed,
  isRightCollapsed,
  isBottomCollapsed,
  onToggleLeft,
  onToggleRight,
  onToggleBottom,
  onSettingsClick,
  onOpenMarketDashboard,
}: TopBarProps) {
  return (
    <div className="flex items-center gap-0 py-1 px-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleLeft}
        className={cn(
          "h-8 w-8 p-0 text-muted-foreground hover:text-foreground hover:bg-ramp-grey-700 transition-colors",
          !isLeftCollapsed && "text-foreground"
        )}
        aria-label="切换左侧栏"
        title="切换左侧栏 (⌘B)"
      >
        <PanelLeft size={16} />
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleBottom}
        className={cn(
          "h-8 w-8 p-0 text-muted-foreground hover:text-foreground hover:bg-ramp-grey-700 transition-colors",
          !isBottomCollapsed && "text-foreground"
        )}
        aria-label="切换底部面板"
        title="切换底部面板 (⌘J)"
      >
        <PanelBottom size={16} />
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleRight}
        className={cn(
          "h-8 w-8 p-0 text-muted-foreground hover:text-foreground hover:bg-ramp-grey-700 transition-colors",
          !isRightCollapsed && "text-foreground"
        )}
        aria-label="切换右侧栏"
        title="切换右侧栏 (⌘I)"
      >
        <PanelRight size={16} />
      </Button>

      <div className="w-px h-5 bg-ramp-grey-700 mx-1" />

      {onOpenMarketDashboard && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onOpenMarketDashboard}
          className="h-8 px-2 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 transition-colors relative group"
          aria-label="市场全景"
          title="市场全景看板 (⌘M)"
        >
          <BarChart3 size={16} className="mr-1" />
          <span className="text-xs font-mono tracking-wider hidden md:inline">全景</span>
          {/* Glow dot */}
          <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse opacity-70" />
        </Button>
      )}

      <div className="w-px h-5 bg-ramp-grey-700 mx-1" />

      <QuickAnalysis />

      <div className="w-px h-5 bg-ramp-grey-700 mx-1" />

      <GlobalModelSelector />

      <div className="w-px h-5 bg-ramp-grey-700 mx-1" />

      <Button
        variant="ghost"
        size="sm"
        onClick={onSettingsClick}
        className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground hover:bg-ramp-grey-700 transition-colors"
        aria-label="打开设置"
        title="打开设置 (⌘,)"
      >
        <Settings size={16} />
      </Button>
    </div>
  );
}
