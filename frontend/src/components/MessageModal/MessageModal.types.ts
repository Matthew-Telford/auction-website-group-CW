export interface Poster {
  id: number;
  name: string;
  email: string;
}

export interface Message {
  id: string;
  message_title: string;
  message_body: string;
  created_at: string;
  poster: Poster | null;
  is_owner: boolean;
  replying_to_id: string | null;
  replies: Message[];
}
