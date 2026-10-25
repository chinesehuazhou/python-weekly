import type {ReactNode} from 'react';

// 样例期正文里只有三种行内标记：链接、行内代码、加粗。
// 为此装 react-markdown 不值当（本分支刚把它卸掉），这里做一个只认这三种的渲染器。
// 不认 HTML 标签是有意的：正文是我们自己的 markdown，不该出现裸 HTML。
const TOKEN = /\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*/g;

export function renderInline(text: string, keyPrefix = 'md'): ReactNode[] {
  const nodes: ReactNode[] = [];
  let last = 0;
  let index = 0;
  let match: RegExpExecArray | null;

  TOKEN.lastIndex = 0;
  while ((match = TOKEN.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }

    const key = `${keyPrefix}-${index++}`;
    if (match[1] && match[2]) {
      nodes.push(
        <a key={key} href={match[2]} target="_blank" rel="noopener noreferrer">
          {match[1]}
        </a>,
      );
    } else if (match[3]) {
      nodes.push(<code key={key}>{match[3]}</code>);
    } else if (match[4]) {
      nodes.push(<strong key={key}>{match[4]}</strong>);
    }

    last = match.index + match[0].length;
  }

  if (last < text.length) {
    nodes.push(text.slice(last));
  }

  return nodes;
}
