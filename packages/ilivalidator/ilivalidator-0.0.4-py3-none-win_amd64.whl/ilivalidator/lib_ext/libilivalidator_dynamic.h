#ifndef __LIBILIVALIDATOR_H
#define __LIBILIVALIDATOR_H

#include <graal_isolate_dynamic.h>


#if defined(__cplusplus)
extern "C" {
#endif

typedef int (*ilivalidator_fn_t)(graal_isolatethread_t*, char*, char*);

#if defined(__cplusplus)
}
#endif
#endif
