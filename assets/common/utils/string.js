export const format = (string, ...args) => {
  string.replace(/{(\d+)}/g, (match, number) => (
    args[number] !== undefined ? args[number] : match
  ));
};

export { format as default };
