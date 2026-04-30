import { BottomPanel } from '@/components/panels/bottom/bottom-panel';
import { LeftSidebar } from '@/components/panels/left/left-sidebar';
import { RightSidebar } from '@/components/panels/right/right-sidebar';
import { TabBar } from '@/components/tabs/tab-bar';
import { TabContent } from '@/components/tabs/tab-content';
import { SidebarProvider } from '@/components/ui/sidebar';
import { FlowProvider, useFlowContext } from '@/contexts/flow-context';
import { LayoutProvider, useLayoutContext } from '@/contexts/layout-context';
import { TabsProvider, useTabsContext } from '@/contexts/tabs-context';
import { useLayoutKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts';
import { cn } from '@/lib/utils';
import { SidebarStorageService } from '@/services/sidebar-storage';
import { TabService } from '@/services/tab-service';
import { ReactFlowProvider } from '@xyflow/react';
import { ReactNode, useCallback, useEffect, useState } from 'react';
import { TopBar } from './layout/top-bar';

// Create a LayoutContent component to access the FlowContext, TabsContext, and LayoutContext
function LayoutContent({ children }: { children: ReactNode }) {
  const { reactFlowInstance } = useFlowContext();
  const { openTab, tabs, activeTabId } = useTabsContext();
  const { isBottomCollapsed, expandBottomPanel, collapseBottomPanel, toggleBottomPanel } = useLayoutContext();

  // Initialize sidebar states from storage service
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(() =>
    SidebarStorageService.loadLeftSidebarState(false)
  );

  const [isRightCollapsed, setIsRightCollapsed] = useState(() =>
    SidebarStorageService.loadRightSidebarState(false)
  );

  // Track actual sidebar widths for dynamic positioning
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(280);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(280);
  const [bottomPanelHeight, setBottomPanelHeight] = useState(300);

  // Check if market dashboard is active
  const isMarketDashboardActive = activeTabId === 'market-dashboard';

  // Auto-collapse sidebars when market dashboard is active, restore when leaving
  const [savedSidebarState, setSavedSidebarState] = useState({ left: false, right: false });
  const [savedBottomState, setSavedBottomState] = useState(false);

  useEffect(() => {
    if (isMarketDashboardActive) {
      // Save current state before collapsing
      setSavedSidebarState({ left: isLeftCollapsed, right: isRightCollapsed });
      setSavedBottomState(isBottomCollapsed);
      setIsLeftCollapsed(true);
      setIsRightCollapsed(true);
      collapseBottomPanel();
    } else {
      // Restore saved state when leaving dashboard
      setIsLeftCollapsed(savedSidebarState.left);
      setIsRightCollapsed(savedSidebarState.right);
      if (!savedBottomState) {
        expandBottomPanel();
      }
    }
  }, [isMarketDashboardActive, collapseBottomPanel, expandBottomPanel]);

  const handleSettingsClick = () => {
    const tabData = TabService.createSettingsTab();
    openTab(tabData);
  };

  const handleOpenMarketDashboard = useCallback(() => {
    const tabData = TabService.createMarketDashboardTab();
    openTab(tabData);
  }, [openTab]);

  // Add keyboard shortcuts for toggling sidebars and fit view
  useLayoutKeyboardShortcuts(
    () => setIsRightCollapsed(!isRightCollapsed), // Cmd+I for right sidebar
    () => setIsLeftCollapsed(!isLeftCollapsed),   // Cmd+B for left sidebar
    () => reactFlowInstance.fitView({ padding: 0.1, duration: 500 }), // Cmd+O for fit view
    undefined, // undo
    undefined, // redo
    toggleBottomPanel, // Cmd+J for bottom panel
    handleSettingsClick, // Shift+Cmd+J for settings
    handleOpenMarketDashboard, // Cmd+M for market dashboard
  );

  // Save sidebar states whenever they change
  useEffect(() => {
    SidebarStorageService.saveLeftSidebarState(isLeftCollapsed);
  }, [isLeftCollapsed]);

  useEffect(() => {
    SidebarStorageService.saveRightSidebarState(isRightCollapsed);
  }, [isRightCollapsed]);

  // Calculate tab bar and bottom panel positioning based on actual sidebar widths
  const getSidebarBasedStyle = () => {
    if (isMarketDashboardActive) {
      return { left: '0px', right: '0px' };
    }
    let left = 0;
    let right = 0;

    if (!isLeftCollapsed) {
      left = leftSidebarWidth;
    }

    if (!isRightCollapsed) {
      right = rightSidebarWidth;
    }

    return {
      left: `${left}px`,
      right: `${right}px`,
    };
  };

  // Calculate main content positioning accounting for tab bar height
  const getMainContentStyle = () => {
    if (isMarketDashboardActive) {
      return { top: '40px', bottom: '0px', left: '0', right: '0', width: 'auto', height: 'auto' };
    }
    const tabBarHeight = 40;
    let top = tabBarHeight;
    let bottom = 0;

    if (!isBottomCollapsed) {
      bottom = bottomPanelHeight;
    }

    return {
      top: `${top}px`,
      bottom: `${bottom}px`,
      left: '0',
      right: '0',
      width: 'auto',
      height: 'auto',
    };
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden relative bg-background">
      {/* Unified Top Row: TabBar + TopBar side by side */}
      <div
        className={cn(
          "absolute top-0 z-40 flex items-stretch h-10 transition-all duration-200",
          isMarketDashboardActive && "transform -translate-y-full opacity-0 pointer-events-none"
        )}
        style={getSidebarBasedStyle()}
      >
        <TabBar className="flex-1 min-w-0" />
        <div className="flex-shrink-0 flex items-center bg-panel border-b border-l border-[var(--tab-border)]">
          <TopBar
            isLeftCollapsed={isLeftCollapsed}
            isRightCollapsed={isRightCollapsed}
            isBottomCollapsed={isBottomCollapsed}
            onToggleLeft={() => setIsLeftCollapsed(!isLeftCollapsed)}
            onToggleRight={() => setIsRightCollapsed(!isRightCollapsed)}
            onToggleBottom={toggleBottomPanel}
            onSettingsClick={handleSettingsClick}
            onOpenMarketDashboard={handleOpenMarketDashboard}
          />
        </div>
      </div>

      {/* Main content area */}
      <main
        className="absolute inset-0 overflow-hidden"
        style={isMarketDashboardActive ? {
          left: '0px',
          right: '0px',
          top: '0px',
          bottom: '0px',
        } : {
          left: !isLeftCollapsed ? `${leftSidebarWidth}px` : '0px',
          right: !isRightCollapsed ? `${rightSidebarWidth}px` : '0px',
          top: '40px',
          bottom: !isBottomCollapsed ? `${bottomPanelHeight}px` : '0px',
        }}
      >
        <TabContent className="h-full w-full" />
      </main>

      {/* Floating left sidebar - hidden when market dashboard is active */}
      <div className={cn(
        "absolute top-0 left-0 z-30 h-full transition-transform",
        (isLeftCollapsed || isMarketDashboardActive) && "transform -translate-x-full opacity-0"
      )}>
        <LeftSidebar
          isCollapsed={isLeftCollapsed}
          onCollapse={() => setIsLeftCollapsed(true)}
          onExpand={() => setIsLeftCollapsed(false)}
          onWidthChange={setLeftSidebarWidth}
        />
      </div>

      {/* Floating right sidebar - hidden when market dashboard is active */}
      <div className={cn(
        "absolute top-0 right-0 z-30 h-full transition-transform",
        (isRightCollapsed || isMarketDashboardActive) && "transform translate-x-full opacity-0"
      )}>
        <RightSidebar
          isCollapsed={isRightCollapsed}
          onCollapse={() => setIsRightCollapsed(true)}
          onExpand={() => setIsRightCollapsed(false)}
          onWidthChange={setRightSidebarWidth}
        />
      </div>

      {/* Bottom panel - hidden when market dashboard is active */}
      <div
        className={cn(
          "absolute bottom-0 z-20 transition-transform",
          (isBottomCollapsed || isMarketDashboardActive) && "transform translate-y-full opacity-0"
        )}
        style={getSidebarBasedStyle()}
      >
        <BottomPanel
          isCollapsed={isBottomCollapsed}
          onCollapse={collapseBottomPanel}
          onExpand={expandBottomPanel}
          onToggleCollapse={toggleBottomPanel}
          onHeightChange={setBottomPanelHeight}
        />
      </div>
    </div>
  );
}

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <SidebarProvider defaultOpen={true}>
      <ReactFlowProvider>
        <FlowProvider>
          <TabsProvider>
            <LayoutProvider>
              <LayoutContent>{children}</LayoutContent>
            </LayoutProvider>
          </TabsProvider>
        </FlowProvider>
      </ReactFlowProvider>
    </SidebarProvider>
  );
}
