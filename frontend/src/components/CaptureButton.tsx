import { useState } from "react";
import { triggerCapture, type CaptureStatus } from "../api/client";

interface CaptureButtonProps {
  onCaptureComplete?: (status: CaptureStatus) => void;
}

export default function CaptureButton({ onCaptureComplete }: CaptureButtonProps) {
  const [status, setStatus] = useState<CaptureStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCapture = async () => {
    setLoading(true);
    setStatus({ status: "capturing", message: "Taking screenshot...", listings_found: 0 });

    try {
      const result = await triggerCapture();
      setStatus(result);
      onCaptureComplete?.(result);
    } catch (err) {
      setStatus({
        status: "error",
        message: err instanceof Error ? err.message : "Capture failed",
        listings_found: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      <button
        onClick={handleCapture}
        disabled={loading}
        className={`
          w-full sm:w-auto px-6 py-4 rounded-2xl font-semibold text-lg
          transition-all active:scale-95 shadow-lg
          ${
            loading
              ? "bg-slate-600 text-slate-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/25"
          }
        `}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            {status?.message ?? "Processing..."}
          </span>
        ) : (
          "Capture Screen"
        )}
      </button>

      {status && !loading && (
        <p
          className={`text-sm ${
            status.status === "done"
              ? "text-emerald-400"
              : status.status === "error"
                ? "text-red-400"
                : "text-slate-400"
          }`}
        >
          {status.message}
          {status.listings_found > 0 && ` (${status.listings_found} found)`}
        </p>
      )}
    </div>
  );
}
