import  useParams } from "react-router-dom";
import { resourceByKey, resourcesForModule } from "../../catalog";
import { ResourceHub, ResourceWorkspace } from "./ResourceWorkspace";

export default function WorkspaceIndex() {
  const { module = "", resourceKey = "" } = useParams();
  const resource = resourceByKey(resourceKey);
  if (resource) return <ResourceWorkspace resource={resource} />;
  const items = resourcesForModule(module);
  return <ResourceHub title={`${module} workspace`} subtitle="Choose a live collection" items={items} />;
}
