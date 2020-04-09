module.exports = {
  title: 'geektime-dl',
  base: '/geektime_dl/',
  description: '把极客时间装进 Kindle',
  head: [
    ['link', { rel: "icon", type: "image/jpg", href: "/favicon.jpg"}]
  ],
  plugins: {
    'baidu-tongji': {
      hm: '7972bc564f84e320d4f261fe1ada61da'
    }
  },
  themeConfig: {
    lastUpdated: '更新于',
    repo: 'jachinlin/geektime_dl',
    repoLabel: 'GitHub',
    docsDir: 'docs',
    editLinks: true,
    editLinkText: '帮助我们改善此页面！',
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide' },
      { text: '招聘', link: '/recruit' }
    ],
    displayAllHeaders: true,
    sidebar: {
      '/': [
        {
          collapsable: false,
          sidebarDepth: 1,
          children: [
            '',
            'tldr',
            'intro',
            'guide',
            'faq',
            'bonus'
          ]
        }
      ]
    }
  }
}