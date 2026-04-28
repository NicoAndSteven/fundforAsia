import { cn } from '@/lib/utils';
import { getStatusColor } from '../utils';

interface OutputNodeStatusProps {
  isProcessing: boolean;
  isAnyAgentRunning: boolean;
  isOutputAvailable: boolean;
  isConnected: boolean;
  onViewOutput?: () => void;
  processingText?: string;
  completingText?: string;
  availableText?: string;
  idleText?: string;
}

export function OutputNodeStatus({
  isProcessing,
  isAnyAgentRunning,
  isOutputAvailable,
  isConnected,
  onViewOutput,
  processingText = "处理中",
  completingText = "完成中",
  availableText = "查看结果",
  idleText = "等待中"
}: OutputNodeStatusProps) {
  const isLocallyProcessing = isProcessing;
  const isGloballyProcessing = !isProcessing && isAnyAgentRunning;
  const hasGradientAnimation = isLocallyProcessing || isGloballyProcessing;
  const isClickable = isOutputAvailable && !isLocallyProcessing && !isGloballyProcessing;
  
  let displayText: string;
  if (isLocallyProcessing) {
    displayText = processingText;
  } else if (isGloballyProcessing) {
    displayText = completingText;
  } else if (isOutputAvailable) {
    displayText = availableText;
  } else {
    displayText = idleText;
  }

  const status = hasGradientAnimation ? 'IN_PROGRESS' : 'IDLE';

  return (
    <div 
      className={cn(
        "text-foreground text-xs rounded p-2 border border-status transition-colors",
        hasGradientAnimation ? "gradient-animation" : getStatusColor(status),
        isClickable && "bg-primary text-primary-foreground cursor-pointer hover:bg-primary/80",
        !isOutputAvailable && !hasGradientAnimation && "opacity-50"
      )}
      onClick={isClickable ? onViewOutput : undefined}
    >
      {hasGradientAnimation ? (
        <div className="flex items-center gap-2 justify-center">
          <span>{displayText}</span>
        </div>
      ) : (
        <span>{displayText}</span>
      )}
    </div>
  );
}