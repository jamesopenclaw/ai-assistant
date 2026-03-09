export interface KnowledgeItem {
  id: string;
  title: string;
  category: 'document' | 'code' | 'api' | 'folder' | 'other';
  tags: string[];
  content: string;
  author: string;
  createdAt: string;
  updatedAt: string;
  views: number;
  status: 'published' | 'draft';
}
