export const prettyPrintCode = () => {
  const wikiPreTags = document.querySelectorAll('.wiki-article pre');

  for (let i = 0; i < wikiPreTags.length; i += 1) {
    const wikiPreTag = wikiPreTags[i];
    wikiPreTag.classList.add('prettyprint');
  }
};

export default {};
