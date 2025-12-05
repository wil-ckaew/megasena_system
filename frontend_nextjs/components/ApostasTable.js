export default function ApostasTable({ results = [] }) {
  if (!Array.isArray(results) || results.length === 0) return null;

  return (
    <div className="w-full">
      <style>{`
        .ball-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 70px;
          height: 70px;
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          border-radius: 50%;
          font-weight: bold;
          font-size: 24px;
          color: white;
          box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
          transition: all 0.3s ease;
          margin: 8px;
          position: relative;
          overflow: hidden;
        }

        .ball-number::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%);
          animation: shine 3s infinite;
        }

        @keyframes shine {
          0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
          100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }

        .ball-number:hover {
          transform: scale(1.15) translateY(-5px);
          box-shadow: 0 20px 40px rgba(99, 102, 241, 0.5);
        }

        .ball-number span {
          position: relative;
          z-index: 1;
        }

        .numbers-container {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 4px;
          padding: 20px 0;
        }

        .summary-text {
          text-align: center;
          color: #9ca3af;
          font-size: 14px;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
      `}</style>

      <div className="numbers-container">
        {results.map((number, index) => (
          <div key={index} className="ball-number">
            <span>{number}</span>
          </div>
        ))}
      </div>

      <div className="summary-text">
        <p>Total: <strong className="text-indigo-300">{results.length}</strong> números sorteados</p>
      </div>
    </div>
  );
}
