/**
 * Markdown message component for rendering formatted chat messages.
 */

'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Box, Typography } from '@mui/material';
import 'highlight.js/styles/github-dark.css';

interface MarkdownMessageProps {
  content: string;
  isUser?: boolean;
}

export default function MarkdownMessage({ content, isUser = false }: MarkdownMessageProps) {
  return (
    <Box
      sx={{
        '& p': {
          margin: 0,
          marginBottom: 1,
          '&:last-child': {
            marginBottom: 0,
          },
        },
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          marginTop: 1,
          marginBottom: 1,
          fontWeight: 600,
        },
        '& h1': { fontSize: '1.75rem' },
        '& h2': { fontSize: '1.5rem' },
        '& h3': { fontSize: '1.25rem' },
        '& h4': { fontSize: '1.1rem' },
        '& h5': { fontSize: '1rem' },
        '& h6': { fontSize: '0.9rem' },
        '& ul, & ol': {
          marginTop: 0.5,
          marginBottom: 1,
          paddingLeft: 3,
        },
        '& li': {
          marginBottom: 0.5,
        },
        '& code': {
          backgroundColor: isUser ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.08)',
          padding: '2px 6px',
          borderRadius: 1,
          fontSize: '0.9em',
          fontFamily: 'monospace',
        },
        '& pre': {
          backgroundColor: '#1e1e1e',
          borderRadius: 1,
          padding: 2,
          overflow: 'auto',
          marginTop: 1,
          marginBottom: 1,
          '& code': {
            backgroundColor: 'transparent',
            padding: 0,
            color: '#d4d4d4',
          },
        },
        '& blockquote': {
          borderLeft: '4px solid',
          borderColor: isUser ? 'rgba(255, 255, 255, 0.4)' : 'primary.main',
          paddingLeft: 2,
          marginLeft: 0,
          marginRight: 0,
          marginTop: 1,
          marginBottom: 1,
          fontStyle: 'italic',
        },
        '& table': {
          borderCollapse: 'collapse',
          width: '100%',
          marginTop: 1,
          marginBottom: 1,
        },
        '& th, & td': {
          border: '1px solid',
          borderColor: isUser ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.12)',
          padding: 1,
          textAlign: 'left',
        },
        '& th': {
          backgroundColor: isUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.04)',
          fontWeight: 600,
        },
        '& a': {
          color: isUser ? 'rgba(255, 255, 255, 0.9)' : 'primary.main',
          textDecoration: 'underline',
          '&:hover': {
            opacity: 0.8,
          },
        },
        '& hr': {
          border: 'none',
          borderTop: '1px solid',
          borderColor: isUser ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.12)',
          marginTop: 2,
          marginBottom: 2,
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // Custom component for paragraphs to use MUI Typography
          p: ({ children }) => (
            <Typography variant="body1" component="p">
              {children}
            </Typography>
          ),
          // Ensure inline code doesn't break Typography
          code: ({ node, className, children, ...props }: any) => {
            const inline = !className;
            if (inline) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
}

