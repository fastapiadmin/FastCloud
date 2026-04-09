/** @param {import("plop").NodePlopAPI} plop */
export default function (plop) {
  plop.setGenerator("curd-list", {
    description: "列表页骨架：PageSearch + PageContent + CrudToolbarLeft/Right + useCrudList",
    prompts: [
      {
        type: "input",
        name: "modulePath",
        message: "views 下路径（如 module_example/demo）",
      },
      {
        type: "input",
        name: "componentName",
        message: "组件 name（PascalCase，如 Demo）",
      },
      {
        type: "input",
        name: "permPrefix",
        message: "权限前缀（如 module_example:demo）",
      },
    ],
    actions: [
      {
        type: "add",
        path: "src/views/{{modulePath}}/index.vue",
        templateFile: "plop-templates/curd-list-page.vue.hbs",
        skipIfExists: true,
      },
    ],
  });
}
