export type Item = {
  id: string;
  title: string;
  description: string;
  minimum_bid: number;
  current_bid: number;
  auction_end_date: Date;
  created_at: Date;
  item_image: string;
};

export type SearchItem = {
  id: string;
  title: string;
};

export type SearchItems = SearchItem[];
