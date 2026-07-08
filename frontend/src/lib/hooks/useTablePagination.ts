"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

export const DEFAULT_TABLE_PAGE_SIZE = 5;

interface UseTablePaginationOptions<T> {
  items: T[];
  pageParam?: string;
  pageSize?: number;
}

export function useTablePagination<T>({
  items,
  pageParam = "page",
  pageSize = DEFAULT_TABLE_PAGE_SIZE
}: UseTablePaginationOptions<T>) {
  const [, setUrlRevision] = useState(0);
  const searchParams = useSearchParams();
  const pageCount = Math.max(1, Math.ceil(items.length / pageSize));
  const rawPage = searchParams.get(pageParam);
  const requestedPage = parsePage(rawPage);
  const currentPage = clamp(requestedPage, 1, pageCount);
  const startIndex = items.length === 0 ? 0 : (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, items.length);
  const pageItems = useMemo(() => items.slice(startIndex, endIndex), [endIndex, items, startIndex]);

  const writePage = useCallback(
    (nextPage: number, mode: "push" | "replace" = "push") => {
      const clampedPage = clamp(nextPage, 1, pageCount);
      const params = new URLSearchParams(searchParams.toString());

      if (clampedPage <= 1) {
        params.delete(pageParam);
      } else {
        params.set(pageParam, String(clampedPage));
      }

      const query = params.toString();
      const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;

      if (mode === "replace") {
        window.history.replaceState(null, "", url);
      } else {
        window.history.pushState(null, "", url);
      }
      setUrlRevision((revision) => revision + 1);
    },
    [pageCount, pageParam, searchParams]
  );

  useEffect(() => {
    const expectedPageParam = currentPage <= 1 ? null : String(currentPage);
    if (rawPage !== expectedPageParam && (rawPage !== null || currentPage > 1)) {
      const params = new URLSearchParams(searchParams.toString());

      if (currentPage <= 1) {
        params.delete(pageParam);
      } else {
        params.set(pageParam, String(currentPage));
      }

      const query = params.toString();
      window.history.replaceState(null, "", query ? `${window.location.pathname}?${query}` : window.location.pathname);
    }
  }, [currentPage, pageParam, rawPage, searchParams]);

  useEffect(() => {
    const syncPageFromHistory = () => setUrlRevision((revision) => revision + 1);
    window.addEventListener("popstate", syncPageFromHistory);
    return () => window.removeEventListener("popstate", syncPageFromHistory);
  }, []);

  return {
    currentPage,
    endIndex,
    pageCount,
    pageItems,
    pageSize,
    setPage: writePage,
    startIndex,
    totalItems: items.length
  };
}

function parsePage(value: string | null) {
  if (!value) {
    return 1;
  }

  const page = Number.parseInt(value, 10);
  return Number.isFinite(page) && page > 0 ? page : 1;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
