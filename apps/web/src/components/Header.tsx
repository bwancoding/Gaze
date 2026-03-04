import React from 'react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title = 'WRHITW', subtitle = "What's Really Happening In The World" }: HeaderProps) {
  return (
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">W</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-neutral-900">{title}</h1>
              <p className="text-xs text-neutral-500 hidden sm:block">{subtitle}</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <a href="/" className="text-neutral-600 hover:text-primary-600 transition-colors">
              首页
            </a>
            <a href="/categories" className="text-neutral-600 hover:text-primary-600 transition-colors">
              分类
            </a>
            <a href="/about" className="text-neutral-600 hover:text-primary-600 transition-colors">
              关于
            </a>
            <button className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors">
              登录
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
