import { Link } from 'react-router-dom';
/** Tactile 3D button. variant: lime(default) | blue | w | red | ink. Renders Link/anchor/button. */
export default function Button({ variant = '', size = '', icon, block, to, href, className = '', children, ...rest }) {
  const cls = ['btn', variant, size, icon ? 'icon' : '', block ? 'block' : '', className].filter(Boolean).join(' ');
  if (to) return <Link to={to} className={cls} {...rest}>{children}</Link>;
  if (href) return <a href={href} className={cls} {...rest}>{children}</a>;
  return <button type="button" className={cls} {...rest}>{children}</button>;
}
