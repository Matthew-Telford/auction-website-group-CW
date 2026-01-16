export interface PaginationConfig {
  currentPage: number;
  totalPages: number;
  maxVisiblePages?: number;
}

export interface PaginationResult {
  visiblePageNumbers: number[];
  showRightEllipsis: boolean;
}

export function calculateVisiblePages(config: PaginationConfig): PaginationResult {
  const { currentPage, totalPages, maxVisiblePages = 3 } = config;

  if (totalPages <= maxVisiblePages) {
    return {
      visiblePageNumbers: Array.from({ length: totalPages }, (_, i) => i + 1),
      showRightEllipsis: false,
    };
  }

  let start = currentPage;
  let end = Math.min(start + maxVisiblePages - 1, totalPages);

  if (end - start + 1 < maxVisiblePages) {
    start = Math.max(1, end - maxVisiblePages + 1);
  }

  const visiblePageNumbers = Array.from({ length: end - start + 1 }, (_, i) => start + i);
  const showRightEllipsis = end < totalPages;

  return {
    visiblePageNumbers,
    showRightEllipsis,
  };
}
