import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      theme="dark"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-surface-300 group-[.toaster]:text-dark-100 group-[.toaster]:border-dark-600 group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-dark-400",
          actionButton:
            "group-[.toast]:bg-primary-500 group-[.toast]:text-dark-900",
          cancelButton:
            "group-[.toast]:bg-dark-600 group-[.toast]:text-dark-300",
          success: "group-[.toaster]:text-success-400",
          error: "group-[.toaster]:text-danger-400",
          warning: "group-[.toaster]:text-warning-400",
          info: "group-[.toaster]:text-primary-400",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
