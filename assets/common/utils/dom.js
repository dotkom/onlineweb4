import { template } from 'underscore';

/**
 * Render a template on the basis of the attributes of a data object
 * @param {object} tmpl A jQuery wrapper DOM object
 * @param {object} context An object containing the template payload
 * @return {object} Rendered DOM subtree containing provided context data
 */
export const render = (tmpl, context) => {
  const node = template(tmpl);
  return node(context);
};

export { render as default };
