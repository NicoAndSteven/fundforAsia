import { Button } from '@/components/ui/button';
import { Card, CardHeader } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { Handle, Position, useReactFlow } from '@xyflow/react';
import { ReactNode, useCallback } from 'react';
import { X } from 'lucide-react';

export interface NodeShellProps {
  id: string;
  selected?: boolean;
  isConnectable?: boolean;
  icon: ReactNode;
  iconColor?: string;
  name: string;
  description?: string;
  children: ReactNode;
  hasLeftHandle?: boolean;
  hasRightHandle?: boolean;
  status?: string;
  width?: string;
}

export function NodeShell({
  id,
  selected,
  isConnectable,
  icon,
  iconColor,
  name,
  description,
  children,
  hasLeftHandle = true,
  hasRightHandle = true,
  status = 'IDLE',
  width = 'w-64',
}: NodeShellProps) {
  const isInProgress = status === 'IN_PROGRESS';
  const reactFlowInstance = useReactFlow();

  const handleDelete = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    reactFlowInstance.deleteElements({ nodes: [{ id }] });
  }, [id, reactFlowInstance]);

  return (
    <div
      className={cn(
        "react-flow__node-default relative group select-none cursor-pointer rounded-xl border transition-all duration-200",
        width,
        !selected && !isInProgress && "border-node bg-node shadow-sm hover:shadow-md hover:border-node-hover",
        selected && !isInProgress && "border-node-selected bg-node shadow-[0_0_0_1px_hsl(var(--node-border-selected)),0_8px_25px_-5px_hsl(var(--node-border-selected)/0.15)]",
        isInProgress && "node-in-progress"
      )}
      data-id={id}
      data-nodeid={id}
    >
      {/* Delete button - visible on hover */}
      <div className="absolute -top-2 -right-2 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
        <Button
          variant="destructive"
          size="icon"
          onClick={handleDelete}
          className="h-5 w-5 rounded-full p-0 shadow-md"
          aria-label="删除节点"
        >
          <X size={10} />
        </Button>
      </div>

      {isInProgress && (
        <div className="animated-border-container" />
      )}
      {hasLeftHandle && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-3.5 !h-3.5 !rounded-full !bg-gray-400 dark:!bg-gray-500 !border-2 !border-background !absolute !left-0 !top-1/2 !-translate-x-1/2 !-translate-y-1/2 z-10 transition-all duration-200 hover:!w-4 hover:!h-4 hover:!shadow-[0_0_6px_2px_hsl(var(--primary)/0.3)]"
          isConnectable={isConnectable}
        />
      )}
      <div className="overflow-hidden rounded-xl">
        <Card className="rounded-none overflow-hidden border-none bg-node">
          <CardHeader className="p-3.5 bg-node flex flex-row items-center space-x-3 rounded-t-sm">
            <div className={cn(
              "flex items-center justify-center h-9 w-9 rounded-xl text-primary-foreground shrink-0",
              isInProgress ? "gradient-animation" : iconColor || "bg-primary/10 text-primary"
            )}>
              {icon}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold text-primary truncate">
                {name || "自定义组件"}
              </div>
              {description && (
                <div className="text-xs text-muted-foreground truncate mt-0.5">
                  {description}
                </div>
              )}
            </div>
          </CardHeader>
          {children}
        </Card>
      </div>
      {hasRightHandle && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-3.5 !h-3.5 !rounded-full !bg-gray-400 dark:!bg-gray-500 !border-2 !border-background !absolute !right-0 !top-1/2 !translate-x-1/2 !-translate-y-1/2 z-10 transition-all duration-200 hover:!w-4 hover:!h-4 hover:!shadow-[0_0_6px_2px_hsl(var(--primary)/0.3)]"
          isConnectable={isConnectable}
        />
      )}
    </div>
  );
}
