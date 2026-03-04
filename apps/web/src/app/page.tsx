'use client';

import React from 'react';
import Header from '../components/Header';
import EventCard from '../components/EventCard';

// 模拟数据（后续会从 API 获取）
const mockEvents = [
  {
    id: '1',
    title: '全球气候峰会达成新协议，各国承诺减少碳排放',
    summary: '为期两周的气候峰会在迪拜落幕，近 200 个国家同意逐步减少化石燃料使用，这是历史上首次明确提及化石燃料的协议。',
    category: '环境',
    sourceCount: 8,
    viewCount: 12453,
    hotScore: 95.8,
    occurredAt: '2026-03-04T10:00:00Z',
  },
  {
    id: '2',
    title: '美联储宣布维持利率不变，通胀压力仍存',
    summary: '美联储联邦公开市场委员会决定将基准利率维持在 5.25%-5.50% 区间，表示将继续密切关注经济数据。',
    category: '财经',
    sourceCount: 6,
    viewCount: 8932,
    hotScore: 87.3,
    occurredAt: '2026-03-04T08:30:00Z',
  },
  {
    id: '3',
    title: '人工智能监管法案在欧盟议会获得通过',
    summary: '欧盟议会以压倒性多数通过《人工智能法案》，将对高风险 AI 系统实施严格监管，科技公司面临新的合规要求。',
    category: '科技',
    sourceCount: 10,
    viewCount: 15678,
    hotScore: 92.1,
    occurredAt: '2026-03-03T16:45:00Z',
  },
  {
    id: '4',
    title: '某国大选结果揭晓，反对党获胜',
    summary: '经过计票，反对党候选人以微弱优势获胜，现任总理承认败选。分析人士称这标志着该国政治格局的重大变化。',
    category: '政治',
    sourceCount: 12,
    viewCount: 23456,
    hotScore: 98.5,
    occurredAt: '2026-03-03T22:00:00Z',
  },
  {
    id: '5',
    title: '新型量子计算机突破，计算速度提升 1000 倍',
    summary: '研究团队宣布在量子纠错方面取得重大进展，新型量子计算机在特定任务上的计算速度比传统超级计算机快 1000 倍。',
    category: '科技',
    sourceCount: 7,
    viewCount: 11234,
    hotScore: 85.6,
    occurredAt: '2026-03-03T14:20:00Z',
  },
  {
    id: '6',
    title: '国际空间站迎来新任务，多国宇航员入驻',
    summary: '来自 5 个国家的 6 名宇航员成功抵达国际空间站，将开展为期 6 个月的科学实验和技术测试。',
    category: '科技',
    sourceCount: 5,
    viewCount: 6789,
    hotScore: 76.4,
    occurredAt: '2026-03-03T05:15:00Z',
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="mb-8">
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-8 text-white">
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              看到完整的故事
            </h1>
            <p className="text-lg md:text-xl text-primary-100 mb-6">
              WRHITW 聚合全球媒体的多视角报道，让你形成独立的判断
            </p>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-bias-left rounded-full"></div>
                <span className="text-sm">左倾视角</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-bias-center rounded-full"></div>
                <span className="text-sm">中立视角</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-bias-right rounded-full"></div>
                <span className="text-sm">右倾视角</span>
              </div>
            </div>
          </div>
        </section>

        {/* Hot Events */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-neutral-900">
              🔥 热门事件
            </h2>
            <div className="flex items-center space-x-2 text-sm text-neutral-600">
              <span>排序：</span>
              <select className="border border-neutral-300 rounded-md px-3 py-1 bg-white">
                <option>热度</option>
                <option>最新</option>
                <option>浏览最多</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockEvents.map((event) => (
              <EventCard key={event.id} {...event} />
            ))}
          </div>
        </section>

        {/* Coming Soon */}
        <section className="mt-12 bg-white rounded-lg border border-neutral-200 p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">
            🚧 开发中
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4">
              <div className="text-3xl mb-2">📰</div>
              <h4 className="font-medium text-neutral-900 mb-1">实时新闻抓取</h4>
              <p className="text-sm text-neutral-600">正在接入更多媒体源</p>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl mb-2">🤖</div>
              <h4 className="font-medium text-neutral-900 mb-1">AI 多视角摘要</h4>
              <p className="text-sm text-neutral-600">预计 Sprint 2 上线</p>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl mb-2">👤</div>
              <h4 className="font-medium text-neutral-900 mb-1">用户系统</h4>
              <p className="text-sm text-neutral-600">收藏、历史记录</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-neutral-200 mt-12 py-8">
        <div className="container mx-auto px-4 text-center text-neutral-600">
          <p className="mb-2">
            WRHITW - What's Really Happening In The World
          </p>
          <p className="text-sm">
            🚧 开发中 • 预计 2026 年 4 月上线
          </p>
        </div>
      </footer>
    </div>
  );
}
