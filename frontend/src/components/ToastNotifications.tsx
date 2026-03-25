/**
 * C-002: Toast Notifications — 4 variante: success/error/warn/info.
 * Wrapper over Ant Design message API for consistent notifications.
 * Common (P1+P2+P3).
 */
import { message } from "antd";
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
} from "@ant-design/icons";

const DURATION = 3; // seconds

export const toast = {
  success: (content: string, duration = DURATION) => {
    message.success({
      content,
      duration,
      icon: <CheckCircleOutlined />,
    });
  },

  error: (content: string, duration = DURATION) => {
    message.error({
      content,
      duration,
      icon: <CloseCircleOutlined />,
    });
  },

  warning: (content: string, duration = DURATION) => {
    message.warning({
      content,
      duration,
      icon: <WarningOutlined />,
    });
  },

  info: (content: string, duration = DURATION) => {
    message.info({
      content,
      duration,
      icon: <InfoCircleOutlined />,
    });
  },
};

export default toast;
