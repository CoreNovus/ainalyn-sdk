import meta from "../../../pages/_meta.ts";
import v1_meta from "../../../pages/v1/_meta.ts";
import v1_api_reference_meta from "../../../pages/v1/api-reference/_meta.ts";
import v1_concepts_meta from "../../../pages/v1/concepts/_meta.ts";
import v1_getting_started_meta from "../../../pages/v1/getting-started/_meta.ts";
import v1_guides_meta from "../../../pages/v1/guides/_meta.ts";
export const pageMap = [{
  data: meta
}, {
  name: "index",
  route: "/",
  frontMatter: {
    "sidebarTitle": "Index"
  }
}, {
  name: "v1",
  route: "/v1",
  children: [{
    data: v1_meta
  }, {
    name: "api-reference",
    route: "/v1/api-reference",
    children: [{
      data: v1_api_reference_meta
    }, {
      name: "api",
      route: "/v1/api-reference/api",
      frontMatter: {
        "sidebarTitle": "API"
      }
    }, {
      name: "builders",
      route: "/v1/api-reference/builders",
      frontMatter: {
        "sidebarTitle": "Builders"
      }
    }, {
      name: "cli",
      route: "/v1/api-reference/cli",
      frontMatter: {
        "sidebarTitle": "CLI"
      }
    }, {
      name: "entities",
      route: "/v1/api-reference/entities",
      frontMatter: {
        "sidebarTitle": "Entities"
      }
    }]
  }, {
    name: "concepts",
    route: "/v1/concepts",
    children: [{
      data: v1_concepts_meta
    }, {
      name: "agent-definition",
      route: "/v1/concepts/agent-definition",
      frontMatter: {
        "sidebarTitle": "Agent Definition"
      }
    }, {
      name: "architecture-overview",
      route: "/v1/concepts/architecture-overview",
      frontMatter: {
        "sidebarTitle": "Architecture Overview"
      }
    }, {
      name: "compiler-not-runtime",
      route: "/v1/concepts/compiler-not-runtime",
      frontMatter: {
        "sidebarTitle": "Compiler Not Runtime"
      }
    }, {
      name: "platform-boundaries",
      route: "/v1/concepts/platform-boundaries",
      frontMatter: {
        "sidebarTitle": "Platform Boundaries"
      }
    }]
  }, {
    name: "getting-started",
    route: "/v1/getting-started",
    children: [{
      data: v1_getting_started_meta
    }, {
      name: "index",
      route: "/v1/getting-started",
      frontMatter: {
        "sidebarTitle": "Index"
      }
    }, {
      name: "installation",
      route: "/v1/getting-started/installation",
      frontMatter: {
        "sidebarTitle": "Installation"
      }
    }, {
      name: "quickstart",
      route: "/v1/getting-started/quickstart",
      frontMatter: {
        "sidebarTitle": "Quickstart"
      }
    }, {
      name: "your-first-agent",
      route: "/v1/getting-started/your-first-agent",
      frontMatter: {
        "sidebarTitle": "Your First Agent"
      }
    }]
  }, {
    name: "guides",
    route: "/v1/guides",
    children: [{
      data: v1_guides_meta
    }, {
      name: "errors",
      route: "/v1/guides/errors",
      frontMatter: {
        "sidebarTitle": "Errors"
      }
    }, {
      name: "modules",
      route: "/v1/guides/modules",
      frontMatter: {
        "sidebarTitle": "Modules"
      }
    }, {
      name: "prompts",
      route: "/v1/guides/prompts",
      frontMatter: {
        "sidebarTitle": "Prompts"
      }
    }, {
      name: "tools",
      route: "/v1/guides/tools",
      frontMatter: {
        "sidebarTitle": "Tools"
      }
    }, {
      name: "validation",
      route: "/v1/guides/validation",
      frontMatter: {
        "sidebarTitle": "Validation"
      }
    }, {
      name: "workflows",
      route: "/v1/guides/workflows",
      frontMatter: {
        "sidebarTitle": "Workflows"
      }
    }, {
      name: "yaml-export",
      route: "/v1/guides/yaml-export",
      frontMatter: {
        "sidebarTitle": "Yaml Export"
      }
    }]
  }]
}];