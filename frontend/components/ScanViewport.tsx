"use client";

import { useCallback, useRef, useState } from "react";

interface Props {
  previewUrl: string | null;
  isLoading: boolean;
  onFileSelected: (file: File) => void;
}

export default function ScanViewport({ previewUrl, isLoading, onFileSelected }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected]
  );

  return (
    <div className="flex flex-col gap-3">
      <div
        className="scan-frame relative flex aspect-square w-full items-center justify-center overflow-hidden rounded-sm bg-panel"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {previewUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={previewUrl} alt="Uploaded CT scan" className="h-full w-full object-contain opacity-90" />
        ) : (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="flex flex-col items-center gap-2 px-6 text-center text-muted transition-colors hover:text-ink"
          >
            <span className="font-mono text-xs uppercase tracking-widest">No scan loaded</span>
            <span className="font-display text-lg text-ink">Drop a CT slice, or click to browse</span>
            <span className="font-mono text-xs text-muted">PNG / JPG</span>
          </button>
        )}

        {isDragging && (
          <div className="absolute inset-0 flex items-center justify-center bg-void/70 font-mono text-sm text-cyan">
            release to load
          </div>
        )}

        {isLoading && <div className="scan-sweep" />}

        <input
          ref={inputRef}
          type="file"
          accept="image/png, image/jpeg"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFileSelected(file);
          }}
        />
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="w-full border border-hairline py-2 font-mono text-xs uppercase tracking-widest text-muted transition-colors hover:border-cyan hover:text-cyan"
      >
        {previewUrl ? "Replace scan" : "Select file"}
      </button>
    </div>
  );
}
