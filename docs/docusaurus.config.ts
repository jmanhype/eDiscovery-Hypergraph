import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'eDiscovery Hypergraph',
  tagline: 'AI-Powered Legal Document Analysis Platform',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://jmanhype.github.io',
  baseUrl: '/eDiscovery-Hypergraph/',

  organizationName: 'jmanhype',
  projectName: 'eDiscovery-Hypergraph',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          editUrl: 'https://github.com/jmanhype/eDiscovery-Hypergraph/tree/main/docs/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    image: 'img/social-card.png',
    navbar: {
      title: 'eDiscovery Hypergraph',
      logo: {
        alt: 'eDiscovery Logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo-dark.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://api.ediscovery-hypergraph.com/graphiql',
          label: 'GraphQL Playground',
          position: 'left',
        },
        {
          href: 'https://github.com/jmanhype/eDiscovery-Hypergraph',
          position: 'right',
          className: 'header-github-link',
          'aria-label': 'GitHub repository',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/getting-started',
            },
            {
              label: 'Architecture',
              to: '/architecture/architecture-overview',
            },
            {
              label: 'API Reference',
              to: '/api/rest-api',
            },
          ],
        },
        {
          title: 'Features',
          items: [
            {
              label: 'AI Analysis',
              to: '/features/ai-analysis',
            },
            {
              label: 'Search & Discovery',
              to: '/features/search',
            },
            {
              label: 'Compliance',
              to: '/features/compliance',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/jmanhype/eDiscovery-Hypergraph',
            },
            {
              label: 'Examples',
              to: '/examples',
            },
            {
              label: 'Support',
              to: '/support',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} eDiscovery Hypergraph. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['elixir', 'python', 'graphql', 'bash', 'yaml'],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'ediscovery-hypergraph',
      contextualSearch: true,
    },
    announcementBar: {
      id: 'support_us',
      content: '⭐️ If you like eDiscovery Hypergraph, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/jmanhype/eDiscovery-Hypergraph">GitHub</a>!',
      backgroundColor: '#fafbfc',
      textColor: '#091E42',
      isCloseable: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;