export default function Logo({ size = 'default' }: { size?: 'small' | 'default' | 'large' }) {
  const sizes = {
    small: { text: 'text-xl', icon: 'w-8 h-8' },
    default: { text: 'text-2xl', icon: 'w-10 h-10' },
    large: { text: 'text-4xl', icon: 'w-16 h-16' }
  };

  return (
    <div className="flex items-center gap-3">
      {/* Logo Icon - 海马图标 */}
      <div className={`${sizes[size].icon} relative`}>
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#60a5fa" />
              <stop offset="50%" stopColor="#a78bfa" />
              <stop offset="100%" stopColor="#f472b6" />
            </linearGradient>
          </defs>
          {/* 海马形状 */}
          <path
            fill="url(#logoGradient)"
            d="M50 10 C30 10 20 30 20 45 C20 60 30 70 35 75 L30 90 L40 80 L45 90 L50 75 L55 90 L60 80 L70 90 L65 75 C70 70 80 60 80 45 C80 30 70 10 50 10 Z M40 35 A5 5 0 1 1 40 45 A5 5 0 1 1 40 35 Z M55 50 Q60 55 55 60 Q45 65 40 55 Q45 50 55 50 Z"
          />
        </svg>
      </div>
      {/* 文字 */}
      <div className="flex flex-col">
        <span className={`font-bold tracking-wider gradient-text ${sizes[size].text}`}>
          HIGHMARK
        </span>
        <span className="text-xs text-gray-400 tracking-widest">海马职加</span>
      </div>
    </div>
  );
}
