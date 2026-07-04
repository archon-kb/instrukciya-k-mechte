// Ассеты из public/ — через BASE_URL: на GitHub Pages сайт живёт не в корне домена.
const asset = (path: string): string => import.meta.env.BASE_URL + path;

const navItems = [
  { label: 'Проводники', href: '#guides' },
  { label: 'Инструкции', href: '#routes' },
  { label: 'Школа', href: '#school' },
  { label: 'Журнал', href: '#journal' }
];

function Header() {
  return (
    <header className="preview-header" aria-label="Шапка сайта">
      <a href="#top" className="preview-brand" aria-label="Инструкция к мечте">
        <span className="preview-brand__mark">
          <span className="preview-brand__mark-icon" aria-hidden="true" />
        </span>
        <span className="preview-brand__name">
          <span>Инструкция</span>
          <span>к мечте</span>
        </span>
      </a>

      <nav className="preview-nav" aria-label="Главная навигация">
        {navItems.map((item) => (
          <a key={item.href} href={item.href}>
            {item.label}
          </a>
        ))}
      </nav>

      <a href="#guides" className="preview-header__cta">
        Выбрать проводника
      </a>
    </header>
  );
}

function HeroCard() {
  return (
    <div className="preview-card" role="group" aria-labelledby="hero-title">
      <img className="preview-card__contours" src={asset('hero-assets/card-contours.svg')} alt="" aria-hidden="true" />
      <img className="preview-card__frame" src={asset('hero-assets/card-frame.svg')} alt="" aria-hidden="true" />

      <div className="preview-card__kicker">
        <span>КЛУБ ПРОВОДНИКОВ</span>
      </div>

      <span className="preview-card__stamp">ИНСТРУКЦИЯ №01</span>

      <h1 id="hero-title" className="preview-card__title">
        <span>Перед</span>
        <span>исполнением —</span>
        <strong>прочесть.</strong>
      </h1>

      <div className="preview-card__rule" aria-hidden="true">
        <img src={asset('hero-assets/line-star.svg')} alt="" />
      </div>

      <p className="preview-card__copy">
        Маршруты, которые ведут люди,
        <br />
        а не витрины туров.
      </p>
    </div>
  );
}

function HeroActions() {
  return (
    <div className="preview-actions" aria-label="Действия первого экрана">
      <a href="#guides" className="preview-button preview-button--primary">
        <span className="preview-button__icon preview-button__icon--spark" aria-hidden="true" />
        <span>Выбрать проводника</span>
      </a>
      <a href="#routes" className="preview-button preview-button--secondary">
        <span className="preview-button__icon preview-button__icon--route" aria-hidden="true" />
        <span>Смотреть инструкции</span>
      </a>
    </div>
  );
}

export default function App() {
  return (
    <main className="preview-page">
      <section id="top" className="preview-hero" aria-label="Первый экран">
        <div className="preview-hero__shade" aria-hidden="true" />
        <div className="preview-stage">
          <Header />
          <HeroCard />
          <HeroActions />
        </div>
      </section>
    </main>
  );
}
